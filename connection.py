from twisted.internet import reactor, protocol

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

    def __init__(self):
        self.peers = {}
        self.unconnectedPeers = {}
        self.peerConnections = {}
        
    def ConnectionCallbacker:
        def __init__(self, mapper, addr):
            self.mapper = mapper
            self.addr = addr

        def SetRealAddress(self, addr):
            self.mapper[self.addr.domainName] = addr

    def ResolveDomainName(self, name):
        d = reactor.resolve(name)
        callbacker = ConnectionCallbacker(self.unconnectedPeers, name)
        d.addCallback(callbacker.SetRealAddress)

    def ConnectPeers(self):
        for name, endpoint in self.unconnectedPeers.items()
            callbacker = ConnectionCallbacker(self.unconnectedPeers, 
                                              endpoint)
            d = reactor.resolve(name)
            d.addCallback(callbacker.SetRealAddress)
