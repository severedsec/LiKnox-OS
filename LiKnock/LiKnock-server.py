__author__ = 'austin'

import subprocess
import time
import iptc
import os

if os.getuid() != 0:
    print("""not root: iptables functions require root privledge those functions will not be executed.
     this mode is for testing only""")


class LiKnockServer:
    """
    LiKnock-Server is designed to establish a listening connection to iptables logs and listen for port knocking sequences
    to signal a client requesting access the server. Upon completion of a designated knocking sequence LiKnock will alter
    IPtables rules in order to allow the client access.
    """
    def __init__(self):
        self.user_pass = {10: [5643, 5644, 5645, 7895, 8634], 11: [3456, 3564, 3764]}  # these numbers are not for production use
        self.user_position = {10: 0, 11: 0}
        self.last_knock_time = {10: None, 11: None}
        self.client_ip = {10: None, 11: None}
        self.average_time = []
        self.log_watch = subprocess.Popen(['tail', '-f', '/var/log/firewall.log'], stdout=subprocess.PIPE)
        self.main()

    def main(self):
        while True:
            x = self.log_watch.stdout.readline().decode('UTF-8')  # todo clear log before reading to prevent accepting an old auth
            start = time.time()

            for items in self.last_knock_time:
                """
                this code block handles timeouts for testing the timeout is 1 this will be adjusted based on testing for internet
                distanced connections
                """

                if self.last_knock_time[items] is not None:
                    if start - self.last_knock_time[items] > 30:
                        self.last_knock_time[items] = 0
                        self.user_position[items] = 0
                        print('attempt timed out')

            port_location = x.find('DPT=')

            if port_location > 0:
                """
                while this block and its sub blocks sort through the log file to determine if a knock occured and if so handle
                it accordingly
                """
                port_end = x[port_location:].find(' ')
                port = int(x[port_location + 4:port_location + port_end])
                user_location = x.find('LEN=')
                user_end = x[user_location:].find(" ")
                user = int(x[user_location + 4:user_location + user_end]) - 20  # todo find second LEN=, the first is 20 larger

                if user in self.user_pass:

                    if port == self.user_pass[user][self.user_position[user]]:
                        src_location = x.find('SRC=')
                        src_end = x[src_location:].find(' ')
                        packet_src = x[src_location + 4:src_location + src_end]

                        if self.user_position[user] == 0:
                            first = time.time()
                            self.client_ip[user] = packet_src

                        if self.client_ip[user] == packet_src:
                            self.last_knock_time[user] = time.time()
                            self.user_position[user] += 1

                            if self.user_position[user] == len(self.user_pass[user]):
                                self.last_knock_time[user] = None
                                self.user_position[user] = 0
                                last = time.time()
                                print('opening ports for {}, auth took {}'.format(self.client_ip[user], ((last - first))))
                                if os.getuid == 0:
                                    self.open_the_gates(22, packet_src)

    # todo: replace with subprocess, its easier to read, less code, and allows setting LOG options at init

    @staticmethod
    def open_the_gates(port, address):
        table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, "INPUT")
        rule = iptc.Rule()
        rule.protocol = 'tcp'
        match = iptc.Match(rule, 'tcp')
        match.dport = port
        rule.add_match(match)
        rule.src = address
        rule.target = iptc.Target(rule, "ACCEPT")
        chain.insert_rule(rule)

def main():
    LiKnockServer()

if __name__ == '__main__':
    main()
