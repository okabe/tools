#!/usr/bin/env python2

from threading import Thread
from Queue import Queue
import urllib2
import sys

proxyq = Queue()
printq = Queue()

def checker():
    while True:
        if proxyq.empty() is not True:
            proxy = "http://{}".format( proxyq.get() )
            url = "http://icanhazip.com"
            proxy_handler = urllib2.ProxyHandler( { "http" : proxy } )
            opener = urllib2.build_opener( proxy_handler )
            urllib2.install_opener( opener )
            printq.put( "[>] Trying {}".format( proxy ) )
            try:
                response = urllib2.urlopen( url, timeout=3 ).readlines()
                for line in response:
                    if line.rstrip( "\n" ) in proxy:
                        printq.put( "[+] Working proxy: {}".format( proxy ) )
                        with open( "working.txt", "a" ) as log:
                            log.write( "{}\n".format( proxy ) )
                        log.close()
            except Exception as ERROR:
                printq.put( "[!] Bad proxy: {}".format( proxy ) )
            proxyq.task_done()

def printer():
    while True:
        if printq.empty() is not True:
            msg = printq.get()
            print msg
            printq.task_done()

if __name__ == "__main__":
    for i in xrange( 40 ):
        proc = Thread( target=checker )
        proc.daemon = True
        proc.start()

    for proxy in open( sys.argv[1], "r" ):
        proxyq.put( proxy.rstrip( "\n" ) )

    proc = Thread( target=printer )
    proc.daemon = True
    proc.start()

    proxyq.join()
    printq.join()
