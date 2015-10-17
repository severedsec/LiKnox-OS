__author__ = 'austin'

import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
user_number = 10
port_sequence = [5643, 5644, 5645, 7895, 8634]  # these numbers are not for production use

start = time.time()

for i in port_sequence:
    s.sendto(('0'*(user_number - 8)).encode('UTF-8'), ('192.168.0.4', i))
    print(i)
    time.sleep(.0001)


end = time.time()
print('auth took {} seconds'.format(end-start))
