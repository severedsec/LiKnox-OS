__author__ = 'austin'

import subprocess
import time
import iptc

class LiKnockServer:
    """
    LiKnock-Server is designed to establish a listening connection to iptables logs and listen for port knocking sequences
    to signal a client requesting access the server. Upon completion of a designated knocking sequence LiKnock will alter
    IPtables rules in order to allow the client access.
    """
    def __init__(self):
        self.open_sequence = [5643, 5644, 5645]
        self.close_sequence = [3465, 3464, 3463]
        self.current_position = 0
        self.last_knock_time = None
        self.client_ip = None
        self.log_watch = subprocess.Popen(['tail', '-f', '/var/log/firewall.log'], stdout=subprocess.PIPE)
        self.main()

    def main(self):
        while True:
            x = self.log_watch.stdout.readline().decode('UTF-8')
            start = time.time()

            if self.last_knock_time is not None:

                if (start - self.last_knock_time) > 30:
                    self.last_knock_time = None
                    self.current_position = 0
                    print('attempt timed out')

            if x.find('iptables:') > 0:  # checks for iptables data
                port_location = x.find('DPT=')

                if port_location > 0:  # ensures data is TCP/UDP
                    port_end = x[port_location:].find(' ')
                    port = int(x[port_location+4:port_location+port_end])
                    ip_location = x.find('SRC=')
                    ip_end = x[ip_location:].find(' ')
                    packet_src = x[ip_location + 4:ip_location + ip_end]
                    if port == self.open_sequence[self.current_position]:
                        if self.current_position == 0:  # testing
                            first = time.time()
                        if self.client_ip == packet_src or self.client_ip is None:
                            self.client_ip = x[ip_location + 4:ip_location + ip_end]
                            self.last_knock_time = time.time()
                            self.current_position += 1
                            if self.current_position == len(self.open_sequence):
                                self.last_knock_time = None
                                self.current_position = 0
                                last = time.time()
                                #print(x[:-1])
                                print('opening ports for {}, auth took {}'.format(self.client_ip, (1/(last - first))))
                                #self.open_the_gates('22', self.client_ip)
                                #self.Close_the_gates('22', self.client_ip)
                            else:
                                pass
                                #print(x[:-1])

            #end = time.time()
            #print(int(1/(end - start)), '/pps')

    def open_the_gates(self, port , address):
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

    def Close_the_gates(self, port, address):
        table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, "INPUT")
        rule = iptc.Rule()
        rule.protocol = 'tcp'
        match = iptc.Match(rule, 'tcp')
        match.dport = port
        rule.add_match(match)
        rule.src = address
        rule.target = iptc.Target(rule, "ACCEPT")
        chain.delete_rule(rule)


def main():
    LiKnockServer()

if __name__ == '__main__':
    main()
