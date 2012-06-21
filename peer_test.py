from twisted.internet import protocol
from util import Log
from util import AppendTimeStamp
from time import time

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
        self.currentIndex = 0

    def connectionMade(self):
        Log.Msg("Connection made")
        self.localHostName = self.factory.localHostName
        self.dataQueue = ['NAME,' + self.localHostName,
                          'SUB,{INTEGER,age,>,1}',
                          'MSG,age=INTEGER:2']
        Log.Msg('Queue length', str(len(self.dataQueue)) )

    def SendData(self):
        Log.Msg('SendData index', str(self.currentIndex))

        if self.currentIndex >= 3:
            return

        data = self.dataQueue[self.currentIndex]
        if self.currentIndex == 2:
            data = AppendTimeStamp(data)

        #self.transport.write(self.dataQueue[self.currentIndex])
        self.transport.write(data)
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
from util import NetInfo

if __name__ == '__main__':
    Log.StartLogging(sys.stdout)
    if len(sys.argv) > 1:
        host_name = sys.argv[1]
    else:
        host_name = 'localhost'

    if len(sys.argv) > 2:
        remote_port = sys.argv[2]
    else:
        remote_port = 10000

    local_name = NetInfo.GetLocalDomainName()

    factory = DummyPeerConnectionFactory(local_name)
    reactor.connectTCP(host_name, remote_port, factory)

    reactor.run()
