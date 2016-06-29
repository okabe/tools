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
    
    sleep( 5 )
