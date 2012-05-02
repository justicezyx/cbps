from twisted.internet import reactor, protocol
from twisted.python import log
import sys
import state_machine as State
import subscription as Sub

class PeerManager:
    """
    Each server has many peers that it should maitain persisitent
    tcp connections.

    These peers are identified by their domain names. The server goes
    through the following steps to establish connections to peers:
    1. resolve domain names to obtain IP addresses
    2. establish tcp connections to peers
        2.1. successfully established connections are recorded
        2.2. failed connections are retried and queued if a certain
        number of trials fail. Will try periodically with a large
        interval time
    3. a connection management protocol is created for each connection
    to maintain operations
    """

    def __init__(self, name = "pan"):
        self.peers = {}
        self.unconnectedPeers = {}
        self.peerConnections = {}
        self.rt = {}
        self.listenPort = 10000
        self.localHostName = name
        self.connectTimeout = 3
        self.retryLimit = 3

    def AddPeer(self, name):
        log.msg('try to add peer: ' + name)
        if not self.peers.has_key(name):
            self.peers[name] = None
            self.unconnectedPeers[name] = None
        
    def ConnectPeers(self):
        for name, connection in self.unconnectedPeers.items():
            factory = PeerConnectionFactory(name, self.localHostName, self)
            connector = reactor.connectTCP(name, self.listenPort, factory, self.connectTimeout)
            connector.remoteHostName = name
            log.msg('Try to connect to ' + name)

        
    def ListenTCP(self):
        factory = PeerConnectionFactory(None, self.localHostName, self)
        reactor.listenTCP(self.listenPort, factory)

    def Register(self, name, connection):
        """
        Drop connection if the other end is already in the connection list
        """
        if self.peerConnections.has_key(name):
            log.msg('Peer ' + name + ' is already connected')
            return False

        connection.remoteDomainName = name

        if self.unconnectedPeers.has_key(name):
            del self.unconnectedPeers[name]
        peerAddr = connection.transport.getPeer()

        self.peers[name] = peerAddr
        self.peerConnections[name] = connection
        self.rt[name] = []
        log.msg("Registered connection for " + name + "@" + str(peerAddr))
        return True
    
    def Unregister(self, name, connection):
        if name is None:
            #the remote host name is unknown then, no records for this connection in the manager
            log.msg("Unregistered an anonymous connection @ " + connection.remoteIP + ":" + str(connection.remotePort))
            return

        self.unconnectedPeers[name] = None
        del self.peerConnections[name]  # remove connection table entry
        del self.rt[name]   # remove routing table entry
        
        log.msg("Unregistered connection for " + name + "@" + connection.remoteIP + ":" + str(connection.remotePort))

    def RecvSUB(self, name, data):
        log.msg('Received subscription: ' + data + 'from ' + name)
        if not Sub.FormatCheck(data):
            self.peerConnections[name].Send('Wrong Subscriptoin format')
            return

        sub = Sub.Subscription(data)
        self.InstallSUB(name, sub)

    def InstallSUB(self, name, sub):
        if self.rt.has_key(name):
            self.rt[name].append(sub)
        else:
            self.rt[name] = [sub]

    def Forward(self, data, recv_from):
        """
        Message have the format as follows:
        [attribute name]=[attribute value type]:[attribute value]|[data content]
        """

        next_hop = []
        assignments = Sub.AttributeAssignment(data.split('|', 1)[0])

        for name in self.rt:
            subs = self.rt[name]
            for sub in subs:
                if sub.Match(assignments):
                    next_hop.append(name)
                    break

        #TODO: this should be added in the final code
        #next_hop.remove(recv_from)   # commented for test purpose
        for host in next_hop:
            self.peerConnections[host].Send(data)

    def RecvMSG(self, data, recv_from):
        self.Forward(data, recv_from)
        #self.Dispatch(data, recv_from)
        #TODO: messages should be forwarded to client manager for dispatching 

class PeerConnection(protocol.Protocol):
    def connectionMade(self):
        log.msg("connection made")

        self.remoteDomainName = self.factory.domainName
        self.localDomainName = self.factory.localDomainName
        self.peerManager = self.factory.peerManager

        peer = self.transport.getPeer()
        self.remoteIP = peer.host
        self.remotePort = peer.port

        self.stateMachine = State.StateMachine(self)
        if self.factory.domainName is None:
            self.stateMachine.Set(State.INIT)
            self.Send('NREQ')
            return

        if not self.factory.peerManager.Register(self.factory.domainName, self):
            self.Send('TERM,duplicate')
            self.CloseConnection()
        else:
            self.stateMachine.Set(State.READY)

    def dataReceived(self, data):
        data = data.strip()
        log.msg('Data received from ' + self.remoteIP + ' ' + str(self.remotePort) )
        log.msg('Data: ' + data)
        output = self.stateMachine.Accept(data)
        if output is not None:
            self.Send(output)
    
    def CloseConnection(self, reason = ''):
        log.msg('Closing connection to ' + 
                self.remoteIP +
                str(self.remotePort))
        log.msg('Reason: ' + reason)
        self.transport.loseConnection()

    def Send(self, data):
        log.msg('Sending data to ' +
                self.remoteIP +
                str(self.remotePort))
        log.msg('Data: ' + data)
        self.transport.write(data)


    def connectionLost(self, reason):
        log.msg('connection lost for ' + self.remoteIP + ' ' + str(self.remotePort) )
        log.msg('reason: ' + reason.getErrorMessage())
        self.factory.peerManager.Unregister(self.remoteDomainName, self)
        
class PeerConnectionFactory(protocol.ServerFactory, protocol.ClientFactory):
    protocol = PeerConnection

    def __init__(self, name, localName, manager):
        self.domainName = name
        self.localDomainName = localName
        self.peerManager = manager
        self.retryCount = 1
        self.retryLimit = manager.retryLimit

    def clientConnectionFailed(self, connector, reason):
        log.msg('Cannot connect to remote host ' + connector.remoteHostName + ' retry count: ' + str(self.retryCount))
        self.retryCount += 1
        if self.retryCount <= self.retryLimit:
            connector.connect()

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    manager = PeerManager()
    #print manager.localHostName
    manager.AddPeer('planetlab1.cnis.nyit.edu')
    manager.ListenTCP()
    manager.ConnectPeers()

    #reactor.listenTCP(10000, protocol.ServerFactory())
    reactor.listenUDP(10000, protocol.DatagramProtocol())
    reactor.run()
