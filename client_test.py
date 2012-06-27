from twisted.internet import reactor, protocol
from util import Log
from util import NetInfo
from util import ComputeDelay
import util
from twisted.python import log

import config
import sys
import random

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
        self.dataQueue = ['NAME,' + self.username]

        for i in xrange(100):
            text = 'MSG,age=INTEGER:' + str(random.randint(1, 100))
            self.dataQueue.append(text)

    def Subscribe(self, sub):
        self.Send(sub)

    def Publish(self, msg):
        msg = util.AppendTimeStamp(msg)
        sefl.Send(msg)

    def Send(self, data):
        self.transport.write(data)
    def SendData(self):
        if self.currentIndex >= len(self.dataQueue):
            return

        data = self.dataQueue[self.currentIndex]
        if self.currentIndex >= 1:
            data = util.AppendTimeStamp(data)

        log.msg('[Client send] ' + data)

        self.Send(data)
        self.currentIndex += 1

        if self.currentIndex < len(self.dataQueue):
            reactor.callLater(1, self.SendData)

    def dataReceived(self, data):
        """ Received data
        The data should comply with the protocol
        TODO: dupplication of nreq data causes closing connection need to remove this restriction
        """
        log.msg('[client receive]' + data)
        reactor.callLater(1, self.SendData)

        if not ',' in data:
            cmd, val = data, ''
        else:
            cmd, val = data.split(',', 1)
        if cmd == 'MSG':
            delay = ComputeDelay(val)
            log.msg('[delay]' + repr(delay))
            return
        return

        if not ',' in data:
            cmd, val = data, ''
        else:
            cmd, val = data.split(',', 1)

        if cmd == 'NREQ':
            self.Send('NAME,' + self.username)
            return

        if cmd == 'MSG':
            delay = ComputeDelay(val)
            log.msg('[delay]' + repr(delay))
            return


    def connectionLost(self, reason):
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
    factory = ClientFactory('zyx1', 'localhost')

    connector = reactor.connectTCP(factory.remoteHostName, config.BR_CLIENT_LISTEN_PORT, factory)
    connector.remoteHostName = factory.remoteHostName

    reactor.run()

