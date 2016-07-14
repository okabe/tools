#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
from multiprocessing import Process, Queue
from random import randint
from time import sleep

import urllib2, re, sys, socket, ssl, signal, argparse

regexes = {
    "email"       : re.compile(( 
                    "([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)" 
                    )),
    
    "emailpass"   : re.compile(( 
                    "([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\:([a-zA-Z0-9!#$"
                    "%&'*+\/=?]+))"
                    )),
    
    "link"        : re.compile(( 
                    "((http[s]?|ftp|telnet|ssh)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|["
                    "!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
                    )),
    
    "ipv4"        : re.compile(( 
                    "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" 
                    )),
    
    "ipv4port"    : re.compile((
                    "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}"
                    ))
}

def matcher( target_url ):
    findings = {
        "email"     : 0,
        "emailpass" : 0,
        "link"      : 0,
        "ipv4"      : 0,
        "ipv4port"  : 0
    }
            
    for line in urllib2.urlopen( target_url ):
        for regex in regexes:
            if re.search( regexes[regex], line ):
                findings[regex] += 1
                        
    for i in findings:
        if findings[i] > 0:
            msg = "\033[32m[+] Found {} {} in {}\033[0m".format( findings[i], i, target_url )
            sendq.put( msg )

def pastebinfetch( url, tracker ):
    soup = Soup( urllib2.urlopen( url ).read() )
    for menu in soup.findAll( "ul", { "class" : "right_menu" } ):
        for li in menu.findAll( "li" ):
            for a in li.findAll( "a" ):
                rawpaste = ( "http://pastebin.com/raw{}".format( a['href'] ) )
                checked = False
                for i in tracker:
                    if rawpaste in i:
                        checked = True
                if checked is False:
                    tracker.append( rawpaste )
                    sendq.put( "\033[34m[-] Checking {}\033[0m".format( rawpaste ) )
                    matcher( rawpaste )

def sprungebrute():
    while True:
        nid = ""
        symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        while len( nid ) < 4:
            n = randint( 0, 35 )
            nid = nid + symbols[n:n + 1]
        try:
            sprunge_url = "http://sprunge.us/{}".format( nid )
            print "[-] Trying {}".format( url )
            sendq.put( "\033[34m[-] Trying {}\033[0m".format( sprunge_url ) )
            matcher( sprunge_url )
        except Exception as ERROR:
            sendq.put( "\033[91m[!] Fetch failed: {}\033[0m".format( ERROR ) )
            sendq.put( "\033[93m[-] Pausing SprungeBrute for 60 seconds\033[0m" )
            sleep( 57 )
        sleep( 3 )

def fetcher( url, tracker ):
    while True:
        sendq.put( "\033[97m[>] Searching...\033[0m" )
        try:
           pastebinfetch( url, tracker )
        except Exception as ERROR:
           sendq.put( "\033[91m[!] Fetch failed: {}\033[0m".format( ERROR ) )
           sendq.put( "\033[93m[-] Pausing PasteFetch for 60 seconds\033[0m" )
           sleep( 57 )
        sleep( 3 )


if __name__ == "__main__":
    
    url        = "http://pastebin.com"
    server     = "irc.blackcatz.org"
    port       = 6697
    enable_ssl = True
    nick       = "pbmon"
    chan       = "#pbspam"
    sendq      = Queue()
    matchq     = Queue()
    tracker    = []
    findings   = []
    procs      = []

    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    sock.settimeout( 2 )
    sock.connect(( server, port ))
    if enable_ssl is True:
        irc = ssl.wrap_socket( sock )
    else:
        irc = sock
    irc.send( "USER {} {} {} :ohaio\n".format( nick, nick, nick ) )
    irc.send( "NICK {}\n".format( nick ) )
    
    """ start pastebin monitor """
    proc = Process( target=fetcher, args=( url, tracker, ) )
    proc.start()
    procs.append( proc )
    
    """ start sprunge bruter """
    proc = Process( target=sprungebrute )
    proc.start()
    procs.append( proc )

    def signal_handler( signal, frame ):
        print "[!] Shutting down"
        for proc in procs:
            proc.terminate()
        sys.exit( 0 )

    signal.signal( signal.SIGINT, signal_handler )
    print "[+] Press Ctrl+C to quit"
    
    inchan = False
    data = ""
    while True:
        
        try:
            data = irc.recv( 2048 )
        except:
            pass
        
        if data.find( "PING :" ) != -1:
            irc.send( "PONG :{}\n".format( data.split( ":" )[1] ) )
            continue

        elif "376" in data and inchan is False:
            irc.send( "JOIN {}\n".format( chan ) )
            inchan = True

        if sendq.empty() is not True and inchan is True:
            line = sendq.get()
            msg = "PRIVMSG {} :{}\n".format( chan, line )
            irc.send( msg )
            print "[>>>] {}".format( msg.rstrip( "\n" ) )
        
        continue
