from mDataStore.dataFeeder.dataComm import dataServer
import socket

hostname = socket.gethostbyname(socket.gethostname())
print('host: {}'.format(hostname))
dsv = dataServer(hostname,8082)
dsv.listen()

