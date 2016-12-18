#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
from time import sleep
import urllib2, re

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


data = {
    "Accept"     : "text/html",
    "User-Agent" : "Mozilla/5.0"
}

def matcher( line ):
    for regex in regexes:
        if re.search( regexes[regex], line ):
            finding = re.findall( regexes[regex], line )
            print " |- Found {} {}".format( regex, finding )

while True:

    threads = []
    request = urllib2.Request( "http://8ch.net/baphomet/catalog.html", headers=data )
    soup = Soup( urllib2.urlopen( request ).read() )
    for thread in soup.findAll( "div", { "class" : "mix" } ):
        for href in thread.findAll( "a" ):
            if "baphomet/res" in href['href'] and href['href'].endswith( "html" ):
                uri = "http://8ch.net{}".format( href['href'] )
                threads.append( uri )

    for thread in threads:
        request = urllib2.Request( thread, headers=data )
        soup = Soup( urllib2.urlopen( request ).read() )
        for span in soup.findAll( "span", { "class" : "subject" } ):
            print "[+] {}".format( span.text )
        for p in soup.findAll( "p" ):
            matcher( p.text )
        
        sleep( 5 )
