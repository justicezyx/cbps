from twisted.internet import reactor, protocol
from twisted.python import log
import sys
from time import time

import state_machine as State
import subscription as Sub
from util import Log
from util import NetInfo
from util import PeerListFile

import config

class PeerManager:
    """
    Each server has many peers that it should maitain persisitent
    tcp connections.

    These peers are identified by their domain names. The server goes
    through the following steps to establish connections to peers:
    1. establish tcp connections to peers
        1.1. successfully established connections are recorded
        1.2. failed connections are retried and queued if a certain
        number of trials fail. Will try periodically with a large
        interval time
    2. a connection management protocol is created for each connection
    to maintain operations
    """

    def __init__(self, name = ""):
        #Log.Msg('PeerManager init')
        self.peers = {}
        self.unconnectedPeers = {}
        self.peerConnections = {}
        self.rt = {}

        self.listenPort = config.BR_PEER_LISTEN_PORT
        self.localHostName = NetInfo.GetLocalDomainName()
        self.connectTimeout = config.BR_CONN_TIMEOUT
        self.retryLimit = config.BR_CONN_RETRY_LIMIT

        self.clientManager = None

    def AddPeerFromFile(self, fname):
        peers = PeerListFile(fname).Get()
        for peer in peers:
            self.AddPeer(peer)

    def AddPeer(self, name):
        #Log.Msg('AddPeer', name)
        if not self.peers.has_key(name) and name != self.localHostName:
            #
            # if this peer is already in the peer list
            # just return and do nothing
            #
            Log.Msg('Added peer', name)
            Log.Msg('Local host name', self.localHostName)

            self.peers[name] = None
            self.unconnectedPeers[name] = None
        
    def ConnectPeers(self):
        for name, connection in self.unconnectedPeers.items():
            Log.Msg('Attempt to connect', name)

            factory = PeerConnectionFactory(name, self.localHostName, self)
            connector = reactor.connectTCP(name, self.listenPort, factory, self.connectTimeout)
            connector.remoteHostName = name

        
    def ListenTCP(self):
        factory = PeerConnectionFactory('', self.localHostName, self)
        reactor.listenTCP(self.listenPort, factory)

    def Register(self, name, connection):
        """ Register [connection] for [name]
        Drop connection if the other end is already in the connection list
        """

        if self.peerConnections.has_key(name):
            Log.Err('[Already Registered', name)
            return False

        connection.remoteDomainName = name

        if self.unconnectedPeers.has_key(name):
            del self.unconnectedPeers[name]

        peerAddr = connection.transport.getPeer()
        self.peers[name] = peerAddr
        self.peerConnections[name] = connection
        self.rt[name] = []

        Log.Msg('[Registered]', name)

        return True
    
    def Unregister(self, name, connection):
        if name is None or name == '':
            #the remote host name is unknown then, no records for this connection in the manager
            #Log.Msg('[Unregistered]', 'Anonymous')
            return

        self.unconnectedPeers[name] = None
        del self.peerConnections[name]  # remove connection table entry
        del self.rt[name]   # remove routing table entry
        #Log.Msg('Unregistered connection to', name)

    def RecvSUB(self, name, data):
        #Log.Msg('[Received subscription]', data, '[From]', name)
        if not Sub.Subscription.FormatCheck(data):
            self.peerConnections[name].Send('[ERR] Invalid subscriptoin format')
            return

        sub = Sub.Subscription(data)
        self.InstallSUB(name, sub)

    def Broadcast(self, data):
        for c in self.peerConnections.values():
            c.Send(data)

    def InstallSUB(self, name, sub):
        if self.rt.has_key(name):
            self.rt[name].append(sub)
        else:
            self.rt[name] = [sub]

    def Publish(self, data):
        #log.msg(data)
        self.Forward(data, None)

    def Forward(self, data, recv_from):
        """ Message have the format as follows:
        [attribute name]=[attribute value type]:[attribute value]|[data content]
        """
        log.msg('[forward]' + data)
        next_hop = []
        assignments = Sub.AttributeAssignment(data.split('|', 1)[0])

        for name in self.rt:
            subs = self.rt[name]
            for sub in subs:
                if sub.Match(assignments):
                    next_hop.append(name)
                    break

        #TODO: this should be added in the final code
        if recv_from in next_hop:
            next_hop.remove(recv_from)   # commented for test purpose

        for host in next_hop:
            self.peerConnections[host].Send('MSG,' + data)

    def ComputeDelay(self, data):
        time_stamp = float(data.split('|', 2)[1])
        now = time()
        return now - time_stamp

    def RecvMSG(self, data, recv_from):
        self.Forward(data, recv_from)
        delay = self.ComputeDelay(data)
        Log.Msg('delay', repr(delay))
        
        #self.Dispatch(data, recv_from)
        #TODO: messages should be forwarded to client manager for dispatching 

class PeerConnection(protocol.Protocol):
    def connectionMade(self):
        #Log.Msg("connection made")
        self.remoteDomainName = self.factory.domainName
        self.localDomainName = self.factory.localDomainName
        self.peerManager = self.factory.peerManager

        peer = self.transport.getPeer()
        self.remoteIP = peer.host
        self.remotePort = peer.port
        self.remoteAddr = peer.host + ':' + str(peer.port)

        self.stateMachine = State.StateMachine(self)
        if self.factory.domainName is None or self.factory.domainName == '':
            self.stateMachine.Set(State.INIT)
            self.Send('NREQ')
            return

        if not self.peerManager.Register(self.factory.domainName, self):
            self.Send('TERM,duplicate')
            self.CloseConnection()
        else:
            self.stateMachine.Set(State.READY)

    def dataReceived(self, data):
        data = data.strip()
        #Log.Msg('Data received from', self.remoteAddr)
        #Log.Data(data)
        output = self.stateMachine.Accept(data)
        if output is not None:
            self.Send(output)
    
    def CloseConnection(self, reason = ''):
        #Log.Msg('Closing connection to', self.remoteAddr)
        #Log.Msg('Reason:', reason)
        self.transport.loseConnection()

    def Send(self, data):
        #Log.Msg('Sending data to', self.remoteAddr)
        #Log.Data(data)
        self.transport.write(data)

    def SendHello(self):
        now = time.time()
        if now >= (self.lastHelloTime + self.helloInterval):
            self.Send('HELLO')
        #TODO: Considering move the keeplive function into a new class

    def RecvHello(self, now):
        #Log.Msg('The remote sends keepalive becon')
        self.lastHelloTime = now
        #TODO: Update the time of sending the next keepalive message

    def connectionLost(self, reason):
        if self.remoteDomainName == '':
            Log.Msg('[Connection Lost]', self.remoteIP, '[Reason]', reason.getErrorMessage())
        else:
            Log.Msg('[Connection Lost]', self.remoteDomainName, '[Reason]', reason.getErrorMessage())

        self.peerManager.Unregister(self.remoteDomainName, self)
        
class PeerConnectionFactory(protocol.ServerFactory, protocol.ClientFactory):
    protocol = PeerConnection

    def __init__(self, name, localName, manager):
        #Log.Msg('PeerConnectionFactory init', name, localName)
        self.domainName = name
        self.localDomainName = localName
        self.peerManager = manager
        self.retryCount = 1
        self.retryLimit = manager.retryLimit

    def clientConnectionFailed(self, connector, reason):
        Log.Err('[Connection Failed]', connector.remoteHostName, 
                '[Reason]', reason.getErrorMessage(),
                '[Retry]', str(self.retryCount))

        self.retryCount += 1
        if self.retryCount <= self.retryLimit:
            connector.connect()

if __name__ == '__main__':
    #Log.StartLogging(open('test.log', 'a'))
    Log.StartLogging(sys.stdout)
    manager = PeerManager()

    manager.AddPeerFromFile('nodes')
    manager.ListenTCP()
    manager.ConnectPeers()

    reactor.run()
