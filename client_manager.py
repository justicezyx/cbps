from twisted.internet import reactor, protocol
from twisted.python import log
import sys
import config

""" This is for the management of clients

Probably will merge PeerManager and ClientManager into one Broker class
"""


class ClientConnection(protocol.Protocol):
    def connectionMade(self):
        log.msg('connectionMade')
        self.clientManager = self.factory.clientManager
        self.clientName = 'Unknown'
    
    def dataReceived(self, data):
        log.msg('dataRecieved: ' + data)
        data = data.strip()
        self.clientManager.Process(data, self)

    def Send(self, data):
        log.msg('Sending data to ' + self.clientName)
        self.transport.write(data)

    def LoseConnection(self, reason):
        log.msg('Closing connection. Reason: ' + reason)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        """ Just for debug use
        Log this event, do nother else
        """
        log.msg('connectionLost for ' + self.clientName)

        #if self.clientName != 'Unknown':
            #self.clientManager.Unregister(self.clientName)

class ClientConnectionFactory(protocol.ServerFactory):
    protocol = ClientConnection

    def __init__(self, manager):
        #self.localHostName = name
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
        

    def ListenTCP(self):
        log.msg('ListenTCP')

        factory = ClientConnectionFactory(self)
        reactor.listenTCP(self.listenPort, factory)

    def Process(self, data, conn):
        log.msg('Process data: ' + data)

        if cmd == 'NAME':
            # register this connection
            if val is None or val == '':
                log.msg('Error: got empty name')
                return

            conn.clientName = val
            return

        if cmd == 'MSG':
            #   Push the message to broker
            #   broker then forward message to peer manager
            #   then is forwarded in to the broekr networks
            #   TODO: messages should be forwarded to peer manager for delivery
            return

        if cmd == 'PULL':
            if conn.clientName == 'Unknown':
                msgs = self.PullAllMessage()
            else:
                msgs = self.PullMessage(conn.clientName)

            for msg in msgs:
                conn.Send('MSG,' + msg)

            return

        if cmd == 'SUB':
            # TODO: this should be forwarded to peermanager for
            return

        if cmd == 'TERM':
            conn.LoseConnection('Terminated by client')
            return
        
        log.msg('Error: unknow command or request ' + cmd)

    def Unregister(self, name):
        """ This function is only called if this connection has been named before

        if name is 'Unknown', 
        that means the connection connecting host "name" has not been recorded
        This will be removed
        """
        #log.msg('Unregister for client ' + name)
        #del self.clients[name]

        #if self.clients.has_key(name):
            #log.msg('Remove connection for ' + name)
            #del self.clients[name]

    def Register(self, name, conn):
        # this will be removed
        log.msg('Register for client ' + name)

        if self.clients.has_key(name):
            log.msg('Client ' + name + ' is already registered')
            conn.LoseConnection('Duplicate clients')
            return

        conn.clientName = name
        self.clients[name] = conn

if __name__ == '__main__':
    manager = ClientManager()
    manager.ListenTCP()

    log.startLogging(sys.stdout)
    reactor.run()
