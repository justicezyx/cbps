from twisted.internet import protocol
from util import Log

""" Dummy peer used for testing PeerManager

Usage:
    1. Run peer_manager.py by typing 'python peer_manager.py'
    2. Run this file
"""

class DummyPeer(protocol.Protocol):
    """ DummyPeer for testing

    Function identically as PeerManager
    Considering inherent from PeerManager
    """
    

class DummyPeerFactory(protocol.ClientFactory):
    protocol = DummyPeer

if __name__ == '__main__':
    pass
