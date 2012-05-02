import socket

TEST_SITE = 'www.google.com'
TEST_PORT = 80

def GetLocalIP():
    """ Get the external IP address of the local machine
    Test connection to a test site
    Then retrieve the local IP address through the socket name
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect((TEST_SITE, TEST_PORT))
        local_ip = s.getsockname()[0]
    except socket.error:
        local_ip = None
    finally:
        del s
    return local_ip

def GetLocalDomainName():
    myip = GetLocalIP()

    try:
        name = socket.gethostbyaddr(myip)[0]
    except socket.herror:
        return None
    return name

if __name__ == '__main__':
    print GetLocalIP()
    print GetLocalDomainName()
    
        
    
