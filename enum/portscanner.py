#!/usr/bin/env python2

""" 
a simple port scanner
"""

from threading import Thread
from Queue import Queue
from time import sleep
from netaddr import IPNetwork
import argparse, socket, sys

targetq = Queue()
printq = Queue()

def checkport( target, port ):
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    sock.settimeout( 1 )
    try:
        sock.connect(( target, port ))
        printq.put( "[+] {}:{} - open".format( target, str( port ) ) )
    except Exception as ERROR:
        printq.put( "[!] {}:{} - closed".format( target, str( port ) ) )

def worker():
    while True:
        if targetq.empty() is not True:
            stub = targetq.get()
            target = stub.split( ":" )[0]
            port = int( stub.split( ":" )[1] )
            checkport( target, port )
            targetq.task_done()

def printer():
    while True:
        if printq.empty() is not True:
            stub = printq.get()
            print stub
            printq.task_done()
        else:
            sleep( 0.25 )

if __name__ == "__main__":
    
    targets = []
    ports = []

    parser = argparse.ArgumentParser( "a simple port scanner" )
    parser.add_argument( "--targets", required=True, help="targets to scan" )
    parser.add_argument( "--ports", required=True, help="ports to check" )
    parser.add_argument( "--threads", required=False, help="number of threads to use" )

    args = vars( parser.parse_args() )

    if args["targets"]:
        if "/" in args["targets"]:
            targets = [ x for x in IPNetwork( args["targets"] ) ]
        elif "," in args["targets"]:
            targets = [ x for x in args["targets"].split( "," ) ]
        else:
            targets.append( args["targets"] )

    if args["ports"]:
        if "-" in args["ports"]:
            startp = int( args["ports"].split( "-" )[0] )
            endp = int( args["ports"].split( "-" )[1] ) + 1
            ports = [ x for x in range( startp, endp ) ]
        elif "," in args["ports"]:
            ports = [ x for x in args["ports"].split( "," ) ]
        else:
            ports.append( args["ports"] )

    for target in targets:
        for port in ports:
            stub = "{}:{}".format( target, port )
            targetq.put( stub )

    if args["threads"]:
        for i in xrange( int( args["threads"] ) ):
            proc = Thread( target=worker )
            proc.daemon = True
            proc.start()
    else:
        proc = Thread( target=worker )
        proc.daemon = True
        proc.start()

    proc = Thread( target=printer )
    proc.daemon = True
    proc.start()

    targetq.join()
    printq.join()

