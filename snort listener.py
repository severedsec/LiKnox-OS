__author__ = 'austin'

#! /usr/bin/env python

import os
import socket
import struct
import time

# from src/decode.h
ALERTMSG_LENGTH=256
SNAPLEN=1500

def main():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)  # instantiates the socket object

    # This format does NOT include the 'Event' struct which is the last element
    # of the _AlertPkt struct in src/output-plugins/spo_alert_unixsock.h
    # Thus, we must truncate the messages ('datain[:fmt_size]') before passing
    # them to struct.unpacket()
    fmt = "%ds9I%ds" % (ALERTMSG_LENGTH, SNAPLEN)
    fmt_size = struct.calcsize(fmt)

    try:
        os.remove("/dev/snort_alert")  # removes the old unix socket file if one exists
    except OSError:
        pass

    s.bind("/dev/snort_alert")  # creates a unix socket
    while True:
        try:
            (datain, addr) = s.recvfrom(4096)
            start_time = time.time()  # testing
            (bmsg, ts_sec, ts_usec, caplen, pktlen, dlthdr, nethdr, transhdr, data, val, bpkt) = \
            struct.unpack(fmt, datain[:fmt_size])  # unpacks the data from a received packet into the variables listed above

            # ######## notes about each variable
            # bmsg      = alert message as byte object decode to UTF-8
            # ts_sec    = appears to be a time of some unknown format
            # ts_usec   = seems to always be 0?
            # caplen    = maybe the length of the stream that was captured. libpcap
            # pktlen    = seems to always be 0?
            # dlthdr    = offset to data layer headers 2
            # netdr     = offset to network layer header 3
            # transdr   = offset to transport layer header 4
            # data      = offset to data(pkt body)?
            # val       = seems to always be 0?
            # pkt       = the packet raising the alert decode to UTF-8 may need further work as there are odd unicode characters

            spkt = bpkt.decode('UTF-8', 'ignore')  # spkt for string packet and bpkt for byte packet. decode the byte format to something human readable
            smsg = bmsg.decode('UTF-8', 'ignore')  # same as above
            print(smsg, '\n', spkt)  # prints both of the above on separate lines

            # optionally, do something with the pcap pkthdr (ts_sec + ts_usec +
            # caplen + pktlen) and packet body (pkt)
            end_time = time.time()
            print('running at a rate of ~{} alerts per second\n'.format(int(1.0/(end_time - start_time))))  # finds the rate of decoding and prints it to the screen
        except struct.error:
            print("bad message? (msglen=%d): %s" % (len(datain)))  # handles the existences of a bad packet


if __name__ == '__main__':  # executes the main program
    main()
