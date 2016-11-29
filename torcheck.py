#!/usr/bin/env python2

import urllib2, sys

try:
    ip = sys.argv[1]
    tor_node = False
    url = "http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv"
    for line in urllib2.urlopen( url ).readlines():
        line = line.rstrip( "\n" )
        if ip in line:
            tor_node = True
            break
    
    if tor_node is False:
        print "[-] {} is not a TOR node".format( ip )
    else:
        print "[+] {} is a TOR node".format( ip )

except:
    print "[!] Wrong syntax: {} <ip>".format( sys.argv[0] )
