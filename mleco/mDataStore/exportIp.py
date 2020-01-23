import socket
import mUtil as uu
ip=socket.gethostbyname(socket.gethostname())

uu.save_obj(ip,'ipBlp',path=r'F:\SISTDAD\MEMPGRP\BMORIER\python')
