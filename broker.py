from twisted.internet import reactor, protocol
import sys

from peer_manager import PeerManager
from client_manager import ClientManager
from util import Log
import config

class Broker:
    def __init__(self):
        """
        Initilize peerManager and clientManager which are responsible for
        managing the connections to peers and clients
        """
        self.peerManager = PeerManager()
        self.clientManager = ClientManager()
        
        self.peerManager.AddPeerFromFile(config.BR_PEER_LIST)
        self.peerManager.ListenTCP()
        self.peerManager.ConnectPeers()

        self.clientManager.ListenTCP()

        self.peerManager.clientManager = self.clientManager
        self.clientManager.peerManager = self.peerManager

if __name__ == '__main__':
    broker = Broker()
    Log.StartLogging(sys.stdout)
    reactor.run()
