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
    

if __name__ == '__main__':
    print NetInfo.GetLocalIP()
    print NetInfo.GetLocalDomainName()
    print NetInfo.TEST_SITE
    print NetInfo.TEST_PORT

    import sys
    Log.StartLogging(sys.stdout)

    Log.Msg('test')
    Log.Err('test')
    
        
    
