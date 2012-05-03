from twisted.internet import reactor, protocol
from util import Log
import config
import sys

""" Client class

This class use persistent TCP connections to communicate with a broker
Specific functions are:
    1. Register subscriptions
    2. Publish messages
    3. Waiting for published messages from the broker
"""

class Client(protocol.Protocol):
    def connectionMade(self):
        """ Made connection to a broker

        A broker's client manager will handle connection establishment
        The listening port of the client manager is 10001
        """
        self.username = self.factory.username
        
    def dataReceived(self, data):
        """ Received data

        The data should comply with the protocol
        """
        if data.split(',', 1)[0] == 'NREQ':
            self.transport.write('NAME,' + self.username)
    
class ClientFactory(protocol.ClientFactory):
    protocol = Client

    def __init__(self, username):
        self.username = username

if __name__ == '__main__':
    Log.StartLogging(sys.stdout)
    factory = ClientFactory('zyx')

    reactor.connectTCP('localhost', config.BR_CLIENT_LISTEN_PORT, factory)
    reactor.run()
