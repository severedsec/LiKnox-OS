__author__ = 'austin'

import nmap
import json

class Handlers:
    """
    a class of static methods used by the main program based on the alerts recieved
    """

    @staticmethod
    def nmap(network_address, scan_type):
        nm = nmap.PortScanner()
        options = {'fast': '-T5 -F', 'slow': '-p0-65535'}
        if scan_type in options:
            scan = options[scan_type]
        else:
            exit(9000)
            print('an invalid scan type was passed to the function')
        results = nm.scan(hosts=network_address, arguments=scan)
        file = open('scan.json', 'w')
        json.dump(results, file, indent=2, sort_keys=True)
        file.close

