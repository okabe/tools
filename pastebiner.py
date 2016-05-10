#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
from multiprocessing import Process, Queue
from time import sleep
import urllib2
import re

url = "http://pastebin.com"

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

def matcher( url, line ):
    for regex in regexes:
        if re.search( regexes[regex], line ):
            finding = re.findall( regexes[regex], line )
            print "[+] Found {} on {}: {}".format( 
                regex,
                url,
                finding
            )

checked = []

while True:
    print "[+] Checking for new pastes"
    """ check pastebin.com """
    soup = Soup( urllib2.urlopen( "http://pastebin.com" ).read() )
    for menu in soup.findAll( "ul", { "class" : "right_menu" } ):
        for li in menu.findAll( "li" ):
            for a in li.findAll( "a" ):
                rawpaste = ( "http://pastebin.com/raw{}".format( a['href'] ) )
                if rawpaste not in checked:
                    checked.append( rawpaste )
                    print "[-] Checking {}".format( rawpaste )
                    for line in urllib2.urlopen( rawpaste ):
                        matcher( rawpaste, line )
    
    """ pastie.org """
    #soup = Soup( urllib2.urlopen( "http://pastie.org/pastes" ).read() )
    #for p in soup.findAll( "p", { "class" : "link" } ):
    #    for pastie in p.findAll( "a" ):
    #        rawpastie = "{}/text".format( pastie['href'] )
    #        if rawpastie not in checked:
    #            checked.append( rawpastie )
    #            for line in urllib2.urlopen( rawpastie ):
    #                matcher( rawpastie, line )
    
    sleep( 5 )
