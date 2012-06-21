from twisted.internet import reactor, protocol
from twisted.python import log
import sys
import config
import subscription as Sub

from util import Log

""" This is for the management of clients
Probably will merge PeerManager and ClientManager into one Broker class
"""


class ClientConnection(protocol.Protocol):
    def connectionMade(self):
        self.clientManager = self.factory.clientManager
        self.clientName = 'Unknown'
        self.Send('NREQ')
    
    def dataReceived(self, data):
        data = data.strip()
        self.clientManager.RecvFromClient(data, self)

    def Send(self, data):
        log.msg(data)
        self.transport.write(data)

    def LoseConnection(self, reason):
        Log.Msg('[closing connection]', reason)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        Log.Msg('[Connection Lost]', '[host]', self.clientName)
        if self.clientName != 'Unknown':
            self.clientManager.Unregister(self.clientName)

class ClientConnectionFactory(protocol.ServerFactory):
    protocol = ClientConnection

    def __init__(self, manager):
        self.clientManager = manager
        
class ClientManager:
    """ Manage client information
    
    Each connection will be persistent TCP connection
    The client needs to indicate its name to the manager to 
    1. register subscriptions
    2. pull messages
    Each side can close the connection by sending a 'TERM' message
    """

    def __init__(self):
        self.clients = {}   # name: connection pairs
        self.subscriptionTable = {} # name: subscription pairs
        self.listenPort = config.BR_CLIENT_LISTEN_PORT
        self.msgQueue = {} # {message_id: message}
        self.msgDestCount = {} # {message_id: dest_count}
        self.clientMsgQueue = {} # {client_name: message_id}

        self.peerManager = None

    def ListenTCP(self):
        factory = ClientConnectionFactory(self)
        reactor.listenTCP(self.listenPort, factory)

    def RecvFromBroker(self, data):
        log.msg('[RecvFromBroker]' + data)
        self.Dispatch(data)

    def Dispatch(self, data):
        log.msg('[Dispatch]' + data)
        next_hop = []
        assignments = Sub.AttributeAssignment(data.split('|', 1)[0])
        #print str(assignments)

        for name, subs in self.subscriptionTable.items():
            for sub in subs:
                #print str(sub)
                if sub.Match(assignments):
                    print 'matched' + str(sub) + str(assignments) + name
                    next_hop.append(name)
                    break

        for host in next_hop:
            print 'next hop' + host + str(len(self.clients))
            print self.clients[host]

            self.clients[host].Send('MSG,' + data)

    def RecvFromClient(self, data, conn):
        if not ',' in data:
            cmd, val = data, ''
        else:
            cmd, val = data.split(',', 1)

        if cmd == 'NAME':
            if val is None or val == '':
                Log.Err('[Empty Name]')
                return

            log.msg('[receive from client val]' + val)
            self.Register(val, conn)
            return

        if cmd == 'MSG':
            #forward message to peer manager
            self.peerManager.Publish(data.split(',', 1)[1])
            return
            
        if cmd == 'SUB':
            self.peerManager.Broadcast(data)
            self.Subscribe(val, conn.clientName)
            return

        if cmd == 'TERM':
            conn.LoseConnection('Terminated by client')
            return

        if cmd == 'NREQ':
            conn.Send('NAME,' + self.peerManager.localHostName)
            return

    def Subscribe(self, sub, subscriber): 
        s = Sub.Subscription(sub)
        if self.subscriptionTable.has_key(subscriber):
            self.subscriptionTable[subscriber].append(s)
        else:
            self.subscriptionTable[subscriber] = [s]
            
    def Unregister(self, name):
        """ This function is only called if this connection has been named before

        if name is 'Unknown', 
        that means the connection connecting host "name" has not been recorded
        This will be removed
        """
        #log.msg('Unregister for client ' + name)
        #del self.clients[name]

        if self.clients.has_key(name):
            Log.Msg('[Unregisterred]', name)
            del self.clients[name]

    def Register(self, name, conn):
        # this will be removed
        Log.Msg('[Registerred]', name)

        if self.clients.has_key(name):
            #Log.Err('[already registerred]', name)
            conn.LoseConnection(name + ' already registerred')
            return

        conn.clientName = name
        self.clients[name] = conn

    def PullAllMessage(self):
        return self.msgQueue.values()

    def PullMessage(self, client_name):
        res = []
        for msg_id in self.clientMsgQueue[client_name]:
            res.append(self.msgQueue[msg_id])

            self.msgDestCount[msg_id] -= 1
            if self.msgDestCount[msg_id] <= 0:
                del self.msgQueue[msg_id]

        return res

if __name__ == '__main__':
    manager = ClientManager()
    manager.ListenTCP()

    log.startLogging(sys.stdout)
    reactor.run()
