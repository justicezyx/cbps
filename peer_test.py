from twisted.internet import protocol
from util import Log

""" Dummy peer used for testing PeerManager

Usage:
    1. Run peer_manager.py by typing 'python peer_manager.py'
    2. Run this file
"""

class DummyPeerConnection(protocol.Protocol):
    """ DummyPeer for testing

    Function identically as PeerManager
    Considering inherent from PeerManager
    """

    def __init__(self):
        self.dataQueue = ['NAME,zyx',
                          'SUB,{INTEGER,age,>,1}',
                          'MSG,age=INTEGER:2']
        self.currentIndex = 0

    def connectionMade(self):
        Log.Msg("Connection made")
        Log.Msg('Queue length', str(len(self.dataQueue)) )
        self.localHostName = self.factory.localHostName

    def SendData(self):
        Log.Msg('SendData index', str(self.currentIndex))

        if self.currentIndex >= 3:
            return

        self.transport.write(self.dataQueue[self.currentIndex])
        self.currentIndex += 1

        if self.currentIndex < 3:
            reactor.callLater(1, self.SendData)

    def dataReceived(self, data):
        Log.Data('[recv]', data)
        reactor.callLater(1, self.SendData)

class DummyPeerConnectionFactory(protocol.ClientFactory):
    protocol = DummyPeerConnection

    def __init__(self, name):
        self.localHostName = name

from twisted.internet import reactor
import sys

if __name__ == '__main__':
    Log.StartLogging(sys.stdout)

    factory = DummyPeerConnectionFactory('zyx')
    reactor.connectTCP('localhost', 10000, factory)

    reactor.run()
