__author__ = 'austin'

import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port_sequence = [5643, 5644, 5645]

start = time.time()
for i in port_sequence:
    s.sendto('0000000000000000000000000000000000000000000000000000000000000000000000'.encode('UTF-8'), ('192.168.0.4', i))
    print(i)
   # time.sleep(.001)

end = time.time()
print('auth took {} seconds'.format(end-start))
