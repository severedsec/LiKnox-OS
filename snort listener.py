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
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    # This format does NOT include the 'Event' struct which is the last element
    # of the _AlertPkt struct in src/output-plugins/spo_alert_unixsock.h
    # Thus, we must truncate the messages ('datain[:fmt_size]') before passing
    # them to struct.unpacket()
    fmt = "%ds9I%ds" % (ALERTMSG_LENGTH, SNAPLEN)
    fmt_size = struct.calcsize(fmt)

    try:
        os.remove("/dev/snort_alert")
    except OSError:
        pass

    s.bind("/dev/snort_alert")
    while True:
        try:
            (datain, addr) = s.recvfrom(4096)
            start_time = time.time()  # testing
            (bmsg, ts_sec, ts_usec, caplen, pktlen, dlthdr, nethdr, transhdr, data, val, bpkt) = \
            struct.unpack(fmt, datain[:fmt_size])
            # bmsg      = alert message as byte object decode to UTF-8
            # ts_sec    = !appears to be a time of some unknown format
            # ts_usec   = !seems to always be 0?
            # caplen    = !maybe the length of the stream that was captured. libpcap
            # pktlen    = !seems to always be 0?
            # dlthdr    = seems to always be 0? offset to data layer headers 2
            # netdr     = seems to always be 14? offset to network layer header 3
            # transdr   = seems to always be 34? offset to transport layer header 4
            # data      = seems to always be 42? offset to data(pkt body)?
            # val       = seems to always be 0?
            # pkt       = the packet raising the alert decode to UTF-8 may need further work as there are odd unicode characters

            spkt = bpkt.decode('UTF-7', 'strict')
            smsg = bmsg.decode('UTF-8', 'ignore')
            print(spkt, '\n')

            # optionally, do something with the pcap pkthdr (ts_sec + ts_usec +
            # caplen + pktlen) and packet body (pkt)
            end_time = time.time()
            print('running at a rate of ~{} alerts per second\n'.format(int(1/(end_time - start_time))))
        except struct.error:
            print("bad message? (msglen=%d): %s" % (len(datain)))


if __name__ == '__main__':
    main()
