import socket

class NetInfo:
    TEST_SITE = 'www.google.com'
    TEST_PORT = 80

    @staticmethod
    def GetLocalIP():
        """ Get the external IP address of the local machine

        Test connection to a test site
        Then retrieve the local IP address through the socket name
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            s.connect((NetInfo.TEST_SITE, NetInfo.TEST_PORT))
            local_ip = s.getsockname()[0]
        except socket.error:
            local_ip = None
        finally:
            del s
        return local_ip

    @staticmethod
    def GetLocalDomainName():
        """ Get the domain name of the local machine

        First the external IP address is obtained through GetLocalIP() function
        Then the domain name is obtained through the socket.gethostbyaddr() function
        """
        myip = NetInfo.GetLocalIP()

        try:
            name = socket.gethostbyaddr(myip)[0]
        except socket.herror:
            return None
        return name

from twisted.python import log    
class Log:
    """ Log class for logging
    Message, Error, Data, StartLogging
    """

    @staticmethod
    def Msg(*msg):
        text = '[MSG] ' + ' '.join(msg)
        log.msg(text)

    @staticmethod
    def Err(*msg):
        text = '[ERR] ' + ' '.join(msg)
        log.msg(text)

    @staticmethod
    def Data(*msg):
        text = '[DATA] ' + ' '.join(msg)
        log.msg(text)

    @staticmethod
    def StartLogging(fd):
        log.startLogging(fd)
    

from subscription import Subscription
class SubFile:
    """ Subscription data file
    Format:
    [subscription source] [subscription]
    ...
    Each subscription source corresponds to one subscription
    Each peer records multiple subscriptions for each subscription source
    """

    def __init__(self, fname):
        self.fname = fname

    def Open(self, fname):
        self.fname = fname

    def Get(self):
        lines = []
        try:
            f = open(self.fname, 'r')
        except IOError:
            Log.Err('Cannot open file', self.fname)
        else:
            lines = [line.strip() for line in f if line.strip() != '']
            f.close()

        res = {}
        for line in lines:
            dname, sub = line.split()
            if res.has_key(dname):
                res[dname] = [Subscription(sub)]
            else:
                res[dname].append(Subscription(sub))
        return res

    def Append(self, src, sub):
        # write data into subscription file
        f = open(self.fname, 'a')
        f.write(' '.join([src, sub]))
        f.write('\n')
        f.close()

    def AppendMultiple(self, pairs):
        # write multiple (src, sub) to the file
        f = open(self.fname, 'a')
        for pair in pairs:
            f.write(' '.join(pair))
            f.write('\n')
        f.close()

class PeerListFile:
    """ Process peer list file
    A file has the format:
    [peer domain name]
    """
    
    def __init__(self, fname):
        self.fname = fname

    def Open(self, fname):
        self.fname = fname

    def Get(self):
        lines = []
        try:
            f = open(self.fname, 'r')
        except IOError:
            Log.Err('Cannot open file', self.fname)
        else:
            lines = [line.strip() for line in f if line.strip() != '']
            f.close()
        return lines

from time import time

def AppendTimeStamp(data, now = None):
    if now is None:
        now = repr(time())
    return data + '|' + now
    
def ComputeDelay(data):
    time_stamp = float(data.split('|', 2)[1])
    now = time()
    return now - time_stamp

if __name__ == '__main__':
    print NetInfo.GetLocalIP()
    print NetInfo.GetLocalDomainName()
    print NetInfo.TEST_SITE
    print NetInfo.TEST_PORT

    import sys
    Log.StartLogging(sys.stdout)

    Log.Msg('test')
    Log.Err('test')
    
    plfile = PeerListFile('nodes')
    print 'nodes file content'
    print plfile.Get()
    
    subfile = SubFile('nodes')
    subfile.Append('aaa', 'bbb')
    subfile.AppendMultiple([('1','11'), ('2', '22')])
