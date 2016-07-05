#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
from multiprocessing import Process, Queue
from time import sleep

import urllib2, re, sys, socket, ssl, signal, argparse

""" 
    this is just a tiny little bot that spams about shit it finds on pastebin (maybe someday 
    even other paste bin sites?)
"""


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

def matcher():
    while True:
        if matchq.empty() is not True:
            tup = matchq.get()
            url = tup[0]
            line = tup[1]
            for regex in regexes:
                if re.search( regexes[regex], line ):
                    finding = re.findall( regexes[regex], line )
                    msg = "[+] Found {} on {}: {}".format( regex, url, finding )
                    sendq.put( msg )
        else:
            sleep( 1 )
            continue

def fetch( url, tracker ):
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
                    sendq.put( "[-] Checking {}".format( rawpaste ) )
                    for line in urllib2.urlopen( rawpaste ):
                        matchq.put( ( rawpaste, line ) )

def fetcher( url, tracker ):
    while True:
        sendq.put( "[>] Checking for new pastes" )
        try:
           fetch( url, tracker )
        except Exception as ERROR:
           sendq.put( "[!] Fetch failed: {}".format( ERROR ) )
           sendq.put( "[-] Sleeping for 60 seconds" )
           sleepytime = 60
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
    
    for i in range( 1, 2 ):
        proc = Process( target=matcher )
        proc.start()
        procs.append( proc )

    proc = Process( target=fetcher, args=( url, tracker, ) )
    proc.start()
    procs.append( proc )

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
            print "[>>>] {}".format( msg )
        
        continue
