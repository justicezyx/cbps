from twisted.internet import reactor, protocol
from twisted.python import log
import sys

""" Client class

This class use persistent TCP connections to communicate with a broker
Specific functions are:
    1. Register subscriptions
    2. Publish messages
    3. Waiting for published messages from the broker
"""

class Client(protocol.Protocol):
    def __init__(self):
        import config
        self.remotePort = config.LISTEN_PORT

    def connectionMade(self):
        """ Made connection to a broker

        A broker's client manager will handle connection establishment
        The listening port of the client manager is 10001
        """
        
if __name__ == '__main__':
    # TODO
    pass
