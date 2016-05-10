#!/usr/bin/env python2

from multiprocessing import Process, Queue
from BeautifulSoup import BeautifulSoup as Soup
import urllib2
import sys

class Checker:
    def __init__( self, proxy ):
        opener = urllib2.build_opener( urllib2.ProxyHandler( { "http" : proxy } ) )
        urllib2.install_opener( opener )
        try:
            for i in urllib2.urlopen( "http://icanhazip.com/" ).readlines():
                print "[+] Working proxy: {}".format( i.rstrip( "\n" ) )
        except Exception as E:
            pass

class Scanner:
    def __init__( self, proxy_list, workers ):
        self.state = {
            "proxies" : Queue()
        }

        for i in xrange( int( workers ) ):
            proc = Process( target=self.worker )
            proc.start()

        for proxy in open( proxy_list, "r" ).readlines():
            self.state["proxies"].put( proxy.rstrip( "\n" ) )

    def worker( self ):
        while True:
            if self.state["proxies"].empty() is not True:
                Checker( self.state["proxies"].get() )

if __name__ == "__main__":
    Scanner( sys.argv[1], 100 )
