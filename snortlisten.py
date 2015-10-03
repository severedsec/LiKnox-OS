__author__ = 'austin'

import os
import socket
import struct
import time
# import subprocess  # to reopen itself as root, call snort, and pass data to handlers
import dataset  # will be used to manipulate mysql


# if os.geteuid() != 0:
#     subprocess.Popen('sudo python3 snortlisten.py') ## todo: needs to find the correct file to execute.
#     exit(0)

class SnortListen:
    """
    this class is used to listen on a unix socket to snort and call the appropriate methods to handle various events
    """
    def __init__(self):

        start_time = time.time()  # testing

        self.socket_path = Configurator.get_variable("socket_path")
        print(Bcolors.OKGREEN + 'socket_path set to {}'.format(self.socket_path) + Bcolors.ENDC)

        self.mysql_path = Configurator.get_variable("mysql_path")
        print(Bcolors.OKGREEN + 'mysql_path set to {}'.format(self.mysql_path) + Bcolors.ENDC)

        self.send_email = Configurator.get_variable("send_email")
        print(Bcolors.OKGREEN + 'send_email set to {}'.format(self.send_email) + Bcolors.ENDC)

        self.email_address = Configurator.get_variable("email_address")  # todo this should probably support a list of addresses
        print(Bcolors.OKGREEN + 'email_address set to {}'.format(self.email_address) + Bcolors.ENDC)

        # builds socket to listen for snort
        self.snort_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            os.remove(self.socket_path)  # removes the old unix socket file if one exists
        except OSError:
            pass

        end_time = time.time()
        print(Bcolors.WARNING + "init currently takes {} seconds".format(end_time - start_time) + Bcolors.ENDC)

        try: # this shouldn't be needed once the run as root is added as that is the cause of the error
            self.snort_socket.bind(self.socket_path)  # creates a unix socket
        except OSError:
            print(Bcolors.FAIL + 'FATAL ERROR: this is most likely because you are not root' + Bcolors.ENDC)
            exit(1)

        # connects to database and all needed tables
        self.database = dataset.connect('sqlite:///test.sldb')  # !!!this is just for testing we will use mysql in production!!!
        self.table = self.database['logs']
        # once socket is made initiate the snort instance to listen to
        # subprocess.Popen(snort ....)

        self.mainloop()

    def mainloop(self):
        """
        this is the main loop of the listener which handles retrieval of data from the unix socket and calling the appropriate
        function to handle the data retrieved

        data format:
        bmsg    = alert message as byte object decode to UTF-8
        ts_sec  = appears to be a time of some unknown format
        ts_usec = seems to always be 0?
        caplen  = maybe the length of the stream that was captured. libpcap
        pktlen  = seems to always be 0?
        dlthdr  = offset to data layer headers 2
        netdr   = offset to network layer header 3
        transdr = offset to transport layer header 4
        data    = offset to data(pkt body)?
        val     = seems to always be 0?
        pkt     = the packet raising the alert decode to UTF-8 may need further work as there are odd unicode characters
        """
        # This format does NOT include the 'Event' struct which is the last element
        # of the _AlertPkt struct in src/output-plugins/spo_alert_unixsock.h
        # Thus, we must truncate the messages ('datain[:fmt_size]') before passing
        # them to struct.unpacket()

        # from src/decode.h
        alertmsg_length = 256
        snaplen = 1500

        fmt = "%ds9I%ds" % (alertmsg_length, snaplen)
        fmt_size = struct.calcsize(fmt)

        while True:
            try:
                (datain, addr) = self.snort_socket.recvfrom(4096)
                start_time = time.time()  # testing
                (bmsg, ts_sec, ts_usec, caplen, pktlen, dlthdr, nethdr, transhdr, data, val, bpkt) = \
                struct.unpack(fmt, datain[:fmt_size])  # unpacks the data from a received packet into the variables listed above

                spkt = bpkt.decode('UTF-8', 'ignore')  # spkt for string packet and bpkt for byte packet. decode the byte
                #                                      ## format to something human readable
                smsg = bmsg.decode('UTF-8', 'ignore')  # same as above

                self.table.insert(dict(alert=smsg, time=ts_sec, packet=spkt))  # todo prevent indefinite logging create cycle time
                self.pass_to(spkt, smsg)

                # optionally, do something with the pcap pkthdr (ts_sec + ts_usec +
                # caplen + pktlen) and packet body (pkt)
                end_time = time.time()
                print('handling at a rate of ~{} alerts per second\n'.format(int(1.0/(end_time - start_time))))  # finds the rate
                #                                                                       ## of decoding and prints it to the screen
            except struct.error:
                print("bad message? (msglen=%d): %s" % (len(datain)))  # handles the existences of a bad packet

    def pass_to(self, spkt, smsg):
        """
        this will be a bit of a project to build. we need to design a rule syntax to be used with the message section of snort
        that lets us parse the message and determine how to handle it things like adjusting firewall. these should be serialized
        or even put into memory depending on size to speed things up.

        this function will pass the data to the appropriate module to handle things like modifying iptables rules,
        emailing alerts, modifying runnning services, scanning a host in the case of local traffic, etc...
        """
        print(smsg, '\n', spkt)  # prints both of the above on separate lines

        if self.send_email is "yes":
            # todo add ability to email whatever addresses are set #! notice this will only be internal addresses for now
            pass

        if "dos on port x" in smsg:  # note: this is a place holder, the format will need to be more systematic
            # send to alter iptables rules to ban excessive use ips and other such things
            pass

class Configurator:
    """
    static methods used to handle config files for snort and the snortlisten class
    """
    @staticmethod
    def get_variable(variable):
        config = open('snortlisten.conf')
        for line in config.readlines():
            if variable in line:
                line = ''.join(line.split())
                ignore, result = line.split("=", 1)
                return result
            else:
                pass

class Bcolors:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m[!] '
    FAIL      = '\033[91m[X] '
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    SnortListen()

if __name__ == '__main__':  # executes the main program
    main()
