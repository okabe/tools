#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
from time import sleep
import urllib2, re, sys

url = "http://pastebin.com"

try:
    logfile = sys.argv[1]
    print "[+] Saving to {}".format( sys.argv[1] )
except Exception as NOLOGFILE:
    print "[!] Results will not be saved!!!"
    logfile = None

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
            msg = "[+] Found {} on {}: {}".format( 
                regex,
                url,
                finding
            )
            print msg
            if logfile is not None:
                with open( logfile, "a" ) as f:
                    f.write( "{}\n".format( msg ) )
                f.close()
            
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
                    print "[-] Checking {}".format( rawpaste )
                    for line in urllib2.urlopen( rawpaste ):
                        matcher( rawpaste, line )

tracker = []
    
while True:
    print "[>] Checking for new pastes"
    """ check pastebin.com """
    try:
        fetch( url, tracker )
    except Exception as ERROR:
        print "[!] Fetch failed: {}".format( ERROR )
        sleepytime = 60
        for i in range( 0, ( sleepytime + 1 ) ):
            sleep( 1 )
            sys.stdout.write( "[-] Sleeping for {} seconds".format( str( sleepytime - i ) ) )
            sys.stdout.flush()
            sys.stdout.write( "\b" * 100 )
    sleep( 2 )
