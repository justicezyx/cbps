from twisted.internet import reactor, protocol
from util import Log
from util import NetInfo
from util import ComputeDelay
import util

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
    def __init__(self):
        self.currentIndex = 0

    def connectionMade(self):
        """ Made connection to a broker
        A broker's client manager will handle connection establishment
        The listening port of the client manager is 10001
        """
        self.username = self.factory.username
        self.factory.connection = self
        self.dataQueue = ['NAME,' + self.username,
                          'SUB,{INTEGER,age,>,1}',
                          'MSG,age=INTEGER:2']

    def Subscribe(self, sub):
        self.Send(sub)

    def Publish(self, msg):
        msg = util.AppendTimeStamp(msg)
        sefl.Send(msg)

    def Send(self, data):
        self.transport.write(data)
        
    def SendData(self):
        if self.currentIndex >= 3:
            return

        data = self.dataQueue[self.currentIndex]
        if self.currentIndex == 2:
            data = util.AppendTimeStamp(data)

        self.Send(data)
        self.currentIndex += 1

        if self.currentIndex < 3:
            reactor.callLater(1, self.SendData)

    def dataReceived(self, data):
        """ Received data
        The data should comply with the protocol
        """
        #print data
        Log.Msg(data)
        reactor.callLater(1, self.SendData)
        return

        if not ',' in data:
            cmd, val = data, ''
        else:
            cmd, val = data.split(',', 1)

        if cmd == 'NREQ':
            self.Send('NAME,' + self.username)
            return

        if cmd == 'MSG':
            log.msg(data)
            delay = ComputeDelay(val)
            return
            

    def connectionLost(self, reason):
        # after lost connection set the connection to None
        self.factory.connection = None
    
class ClientFactory(protocol.ClientFactory):
    protocol = Client

    def __init__(self, username, remote_name):
        self.username = username
        self.remoteHostName = remote_name

        self.retryCount = 0
        self.retryLimit = 3

        self.connection = None

    def clientConnectionFailed(self, connector, reason):
        self.retryCount += 1
        Log.Err('[Connection failed]', connector.remoteHostName,
                '[reason]', reason.getErrorMessage(),
                '[retry]', str(self.retryCount))

        if self.retryCount < self.retryLimit:
            connector.connect()

def Connect(remote_host = 'localhost', remote_port = config.BR_CLIENT_LISTEN_PORT):
    factory = ClientFactory(NetInfo.GetLocalDomainName(), remote_host)
    connector = reactor.connectTCP(factory.remoteHostName, remote_port, factory)
    connector.remoteHostName = factory.remoteHostName
    return factory
    
if __name__ == '__main__':
    Log.StartLogging(sys.stdout)
    factory = ClientFactory('zyx', 'localhost')

    connector = reactor.connectTCP(factory.remoteHostName, config.BR_PEER_LISTEN_PORT, factory)
    connector.remoteHostName = factory.remoteHostName

    reactor.run()
