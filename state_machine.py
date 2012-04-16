import sys
import connection
from twisted.python import log

class State:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def Create(state, connection):
        dispatcher = state + 'State'
        #print 'dispatcher: ' + dispatcher
        thismodule = sys.modules[__name__]

        try:
            c = getattr(thismodule, dispatcher)
        except AttributeError:
            #print 'return init state'
            return InitState(connection)
        else:
            return c(connection)

    def Transition(self, data):
        command, input = data.split(',', 1)
        handler = 'Handle' + command
        log.msg('Calling ' + handler)
        
        try:
            h = getattr(self, handler)
        except AttributeError:
            return None, self
        else:
            return h(input)

    def HandleDefault(self, data):
        #print data
        return data, self


    def HandleTERM(self, data):
        #print data
        self.connection.CloseConnection('Terminated by remote host')
        return None, self

# state names
INIT = 'Init'
READY = 'Ready'

class InitState(State):
        
    def HandleSUB(self, data):
        # handle received subscription
        # can process only in Ready state
        return None, self

    def HandleNAME(self, data):
        # handle received name
        self.connection.factory.peerManager.Register(
                data, self.connection)
        return None, State.Create(READY, self.connection)

    def HandleNAMEREQ(self, data):
        self.connection.Send('NAME,' + self.connection.factory.localDomainName)
        return None, self
        
class ReadyState(State):
    def HandleSUB(self, data):
        log.msg('Received subscription: ' + data)
        #self.connection.RecvSUB(data)
        self.connection.factory.peerManager.RecvSUB(self.connection.remoteDomainName, data)
        return None, self

class StateMachine:

    def __init__(self, connection):
        self.connection = connection
        self.state = State.Create(INIT, connection)

    def Accept(self, data):
        if not ',' in data:
            out = 'Wrong format'
            return out

        out, newstate = self.state.Transition(data)
        self.state = newstate
        return out

    def Set(self, state):
        log.msg('Setting state to ' + state)
        self.state = State.Create(state, self.connection)

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    connection = connection.PeerConnection()
    m = StateMachine(connection)
    m.Accept('Default,b')
    m.Set(READY)
