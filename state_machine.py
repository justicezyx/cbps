""" This is the state machine class for broker to maintain peering state

This is not a general state machine implementation for all protocols
TODO: Revise this into a different name
"""

import sys
import peer_manager
from twisted.python import log
from util import Log
import time

class State:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def Create(state, connection):
        dispatcher = state + 'State'
        thismodule = sys.modules[__name__]

        try:
            c = getattr(thismodule, dispatcher)
        except AttributeError:
            #print 'return init state'
            return InitState(connection)
        else:
            return c(connection)

    def Transition(self, data):
        if not ',' in data:
            command, input = data, None
        else:
            command, input = data.split(',', 1)

        handler = 'Handle' + command
        
        try:
            h = getattr(self, handler)
        except AttributeError:
            Log.Msg('Calling HandleDefault')
            return self.HandleDefault(data)
        else:
            Log.Msg('Calling ' + handler)
            return h(input)

    def HandleDefault(self, data):
        self.connection.Send('Unknown request')
        self.connection.CloseConnection('Unkown request')
        return None, self

    def HandleTERM(self, data):
        self.connection.CloseConnection('Terminated by remote host')
        return None, self

    def HandelHELLO(self, data):
        self.connection.Alive(time.time())
        self.connection.Send('HELLOACK')
        return None, self

INIT = 'Init'
READY = 'Ready'

class InitState(State):
    def HandleNAME(self, data):
        self.connection.factory.peerManager.Register(data, self.connection)
        return None, State.Create(READY, self.connection)

    def HandleNREQ(self, data):
        self.connection.Send('NAME,' + self.connection.factory.localDomainName)
        return None, self
        
class ReadyState(InitState):
    def HandleSUB(self, data):
        self.connection.peerManager.RecvSUB(self.connection.remoteDomainName, data)
        return None, self

    def HandleMSG(self, data):
        self.connection.peerManager.RecvMSG(data, self.connection.remoteDomainName)
        return None, self

class StateMachine:
    def __init__(self, connection):
        self.connection = connection
        self.state = State.Create(INIT, connection)

    def Accept(self, data):
        out, newstate = self.state.Transition(data)
        self.state = newstate
        return out

    def Set(self, state):
        Log.Msg('Setting state to ' + state)
        self.state = State.Create(state, self.connection)

if __name__ == '__main__':
    Log.StartLogging(sys.stdout)
    m = StateMachine(None)
    m.Accept('DEFAULT')
    m.Set(READY)
