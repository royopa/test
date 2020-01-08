#https://github.com/realpython/materials/tree/master/python-sockets-tutorial
import sys
import socket
import selectors
import types
import queue
import pickle
import mUtil as uu
DEBUG=False
from mUtil import Dict
import time
import numpy as np
M=100000
class baseClientServer():

    def __init__(self):
        self.sel = selectors.DefaultSelector()
        self.send=Dict()
        self.send.q = {}
        self.send.p = {} #restos
        self.rec=Dict()
        self.rec.r = {}
        self.rec.ri = {}
        self.rec.q = {}
        self.addr=[]
        self.N=0

    def service_connection(self, key, mask):
        sock = key.fileobj
        a,conn = key.data
        if not a in self.rec.r:
            self.rec.r[a] = b''
            self.rec.ri[a] = b''
            self.rec.q[a] = queue.Queue()

        if mask & selectors.EVENT_READ:
            if len(self.rec.ri[a]) == 8:
                N = int.from_bytes(self.rec.ri[a], 'big')
            else:
                nHead = 8 - len(self.rec.ri[a])
                try:
                    recv_data = sock.recv(nHead)
                    if not recv_data:
                        print("closing connection", a)
                        self.sel.unregister(sock)
                        sock.close()

                except Exception as e:
                    print('Error while reading socket 1')
                    uu.printException(e)
                    if a in self.addr:
                        self.addr.remove(a)
                    else:
                        print('Closed socket was not in addr list')
                    self.endConnection(a,conn)

                    return
                self.rec.ri[a] += recv_data  # Should be ready to read
                if DEBUG:
                    if len(recv_data) > 0:
                        print('recv {} - ri {}'.format(len(recv_data), len(self.rec.ri[a])))

                if len(self.rec.ri[a]) == 8:
                    N = int.from_bytes(self.rec.ri[a], 'big')
                    self.N=N
            if len(self.rec.ri[a]) == 8:
                try:
                    recv_data1 = sock.recv(N)
                    if not recv_data1:
                        print("closing connection", a)
                        self.sel.unregister(sock)
                        sock.close()
                except Exception as e:
                    print('Error while reading socket 2')
                    uu.printException(e)
                    if a in self.addr:
                        self.addr.remove(a)
                    else:
                        print('Closed socket was not')
                    self.endConnection(a,conn)
                    return
                self.rec.r[a] += recv_data1  # Should be ready to read
                if DEBUG:
                    print('recv1 {} N {}'.format(len(recv_data1), N))

                if len(self.rec.r[a]) == N:
                    self.rec.ri[a] = b''
                    obj = pickle.loads(self.rec.r[a])
                    if DEBUG:
                        print('obj: {}'.format(obj))
                    # self.rec.q[a].put(obj)
                    self.rec.r[a] = b''
                    self.onReceive(a,obj)
            # print("received", repr(recv_data), "from connection", a)

        if mask & selectors.EVENT_WRITE:
            if a in self.send.q and self.send.p[a]:
                try:
                    sent = sock.send(self.send.p[a])  # Should be ready to write
                except Exception as e:
                    print('Error while writing socket 1')
                    uu.printException(e)
                    if a in self.addr:
                        self.addr.remove(a)
                    else:
                        print('Closed socket was not')
                    self.endConnection(a,conn)
                    return
                self.send.p[a] = self.send.p[a][sent:]

            elif a in self.send.q and not self.send.q[a].empty():
                data1 = self.send.q[a].get()
                pdata1 = pickle.dumps(data1)
                try:
                    sent = sock.send(len(pdata1).to_bytes(8, 'big') + pdata1)  # Should be ready to write
                except Exception as e:
                    print('Error while writing socket 1')
                    uu.printException(e)
                    if a in self.addr:
                        self.addr.remove(a)
                    else:
                        print('Closed socket was not')
                    self.endConnection(a,conn)
                    return

                self.send.p[a] += pdata1[sent:]

    def putData(self,v,addrs=None):
        if addrs is None:
            addrs=self.addr
        for a in addrs:
            if not a in self.send.q:
                self.send.q[a] = queue.Queue()
                self.send.p[a] = bytes()
            self.send.q[a].put(v)

    def endConnection(self,addr,conn):
        print("closing connection to", addr)
        self.onEndConnection(addr,conn)
        try:
            self.sel.unregister(conn)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{addr}: {repr(e)}",
            )

        try:
            conn.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            conn = None

    def onReceive(self,addr,obj):
        pass

    def onEndConnection(self,addr,conn):
        pass

    def onListen(self):
        pass


class dataServer(baseClientServer):

    def __init__(self,host,port):
        super(dataServer,self).__init__()
        self.conn=[]

        self.host=host
        self.port=port
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, port))
        lsock.listen()
        # print("listening on", (host, port))
        lsock.setblocking(False)
        self.sock=lsock
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(self.sock, events, data=None)


    def accept_wrapper(self,sock):
        conn, addr = sock.accept()  # Should be ready to read
        self.conn.append(conn)
        self.addr.append(addr)
        print("accepted connection from", addr)
        conn.setblocking(False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=(addr,conn))


    def listen(self,sleepTime=0.00001):
        import time
        t0=time.time()
        i=0
        self.stopListen=False
        try:
            while not self.stopListen:
                self.onListen()
                if sleepTime>0:
                    time.sleep(sleepTime)

                # if DEBUG==True:
                #     t1 = time.time()
                #     if t1-t0>2:
                #         v={'a':np.ones(M,)*i}
                #         print('putData: {}'.format(v))
                #         self.putData(v)
                #         i+=1
                #         t0=t1
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except Exception as e:
            print('Exception. Closing Socket')
            uu.printException(e)
            try:
                self.sel.unregister(self.sock)
            except Exception as e:
                print(
                    f"error: selector.unregister() exception for",
                    f"{self.host}:{self.port} ",
                )
                uu.printException(e)

            try:
                self.sock.close()
            except OSError as e:
                print(
                    f"error: socket.close() exception for",
                    f"{self.host}:{self.port} ",
                )
                uu.printException(e)
            finally:
                # Delete reference to socket object for garbage collection
                self.sock = None
            #KeyboardInterrupt
            # print("caught keyboard interrupt, exiting")






class dataClient(baseClientServer):

    def __init__(self,server_addr):
        #server addr is (host,port)
        super(dataClient,self).__init__()

        for a in server_addr:
            self.start_connection(a)


    def start_connection(self,server_addr):
        # server_addr = (host, port)
        # for i in range(0, num_conns):
        #     connid = i + 1
        print("starting connection to", server_addr)
        self.addr.append(server_addr)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        try:
            sock.connect_ex(server_addr)
        except Exception as e:
            print('Error Connection - Client')
            print('Unable to connect to {}',server_addr)
            uu.printException(e)
            return
        # if errno!= 0:
        #     print('Unable to connect to {}. Errno: {}',server_addr,errno)
        #     return

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sock=sock
        self.sel.register(sock, events, data=(server_addr,sock))
        self.rec.r[server_addr] = b''
        self.rec.ri[server_addr] = b''
        self.rec.q[server_addr] = queue.Queue()



    def listen(self,sleepTime=0.00001):
        import time
        t0=time.time()
        i=0
        self.stopListen=False
        try:
            while not self.stopListen:
                self.onListen()
                if sleepTime>0:
                    time.sleep(sleepTime)
                # if DEBUG==True:
                #     t1 = time.time()
                #     if t1-t0>2:
                #         v={'a':np.ones(M,)*i}
                #         print('putData: {}'.format(v))
                #         self.putData(v)
                #         i+=1
                #         t0=t1
                events = self.sel.select(timeout=1)
                if events:
                    for key, mask in events:
                        self.service_connection(key, mask)
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break
        except Exception as e:
            print('Client Exception')
            uu.printException(e)
            #KeyboardInterrupt
            # print("caught keyboard interrupt, exiting")



