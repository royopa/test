from mDataStore.dataFeeder import blpFeederServer
import socket

hostname = socket.gethostbyname(socket.gethostname())
print('host: {}'.format(hostname))



server = blpFeederServer(hostname,8021)

server.listen()