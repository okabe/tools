#!/usr/bin/env python2

import urllib2, sys, argparse

parser = argparse.ArgumentParser( "torcheck" )
parser.add_argument( "--file", "-f", required=False, help="file of ipv4s" )
parser.add_argument( "--ipv4", "-i", required=False, help="ipv4 to check" )
parser.add_argument( "--verbose", "-v", required=False, action="store_true", help="enable verbosity" )

args = vars( parser.parse_args() )
url = "http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv"
    
try:
    tor_nodes = [ x for x in urllib2.urlopen( url ).readlines() ]
except:
    print "[!] Cannot pull down current TOR node list"
    sys.exit()
    
if args["ipv4"]:
    is_node = False
    for node in tor_nodes:
        if args["ipv4"] in node:
            print "[+] {} is a TOR node".format( args["ipv4"] )
            is_node = True
            break
    
    if args["verbose"]:
        if is_node is False:
            print "[-] {} is not a TOR node".format( args["ipv4"] )
        
elif args["file"]:
    for ip in open( args["file"], "r" ).readlines():
        ip = ip.rstrip( "\n" )
        is_node = False
        for node in tor_nodes:
            if ip in node:
                print "[+] {} is a TOR node".format( ip )
                is_node = True
                break
        
        if args["verbose"]:
            if is_node is False:
                print "[-] {} is not a TOR node".format( ip )

else:
    print "[-] Specify args..."
