#!/usr/bin/env python

"""
Example using stdio, Deferreds, LineReceiver and twisted.web.client.

Note that the WebCheckerCommandProtocol protocol could easily be used in e.g.
a telnet server instead; see the comments for details.

Based on an example by Abe Fettig.
"""

from twisted.internet import stdio, reactor
from twisted.protocols import basic
import client

class ClientConsole(basic.LineReceiver):
    delimiter = '\n' # unix terminal style newlines. remove this line
                     # for use with Telnet

    def __init__(self, remote_host = 'localhost', remote_port = 10001):
        self.connector = client.Connect(remote_host, remote_port)
        self.remoteHostName = remote_host
        self.remotePort = remote_port

    def connectionMade(self):
        self.sendLine('Client console. Type "help" for help.')
        self.sendLine('Remote server: ' + self.remoteHostName)

    def lineReceived(self, line):
        # Ignore blank lines
        if not line: return

        # Parse the command
        commandParts = line.split()
        command = commandParts[0].lower()
        args = commandParts[1:]

        # Dispatch the command to the appropriate method.  Note that all you
        # need to do to implement a new command is add another do_* method.
        try:
            method = getattr(self, 'do_' + command)
        except AttributeError, e:
            self.sendLine('Error: no such command.')
        else:
            try:
                method(*args)
            except Exception, e:
                self.sendLine('Error: ' + str(e))

    def do_help(self, command=None):
        """help [command]: List commands, or show help on the given command"""
        if command:
            self.sendLine(getattr(self, 'do_' + command).__doc__)
        else:
            commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
            self.sendLine("Valid commands: " +" ".join(commands))

    def do_quit(self):
        """quit: Quit this session"""
        self.sendLine('Goodbye.')
        self.transport.loseConnection()
        
    def do_send(self, data):
        if self.connector.connection is None:
            self.sendLine('Connection not established')
            return

        self.connector.connection.Send(data)
        
    def do_nreq(self, data):
        self.connector.connection.Send('NREQ')

    def do_connect(self, data = None):
        if self.connector.connection is None:
            self.connector = client.Connect(self.remoteHostName, self.remotePort)

    def connectionLost(self, reason):
        # stop the reactor, only because this is meant to be run in Stdio.
        if reactor.running:
            reactor.stop()

if __name__ == "__main__":
    stdio.StandardIO(ClientConsole())
    reactor.run()
