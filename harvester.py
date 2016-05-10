#!/usr/bin/env python2

from random import choice
from time import sleep
from BeautifulSoup import BeautifulSoup as Soup
import requests
import sys
import re

class Google:
    """ scrape google search results """
    def __init__( self, site, minsleep, maxsleep, maxpage ):
        self.config = {
            "site"     : site,
            "minsleep" : minsleep,
            "maxsleep" : maxsleep,
            "maxpage"  : maxpage,
            "agents"   : None
        }

        self.state = {
            "opener"    : None,
            "response"  : None,
            "links"     : [],
            "pagecount" : 0
        }

        self.headers = {
            "User-agent" : None
        }

        self.filecounts = {
            "exe" : 0,
            "txt" : 0,
            "doc" : 0,
            "docx" : 0,
            "docm" : 0,
            "dotx" : 0,
            "dotm" : 0,
            "log"  : 0,
            "rtf"  : 0,
            "wpd"  : 0,
            "wps"  : 0,
            "123"  : 0,
            "app"  : 0,
            "csv"  : 0,
            "zip"  : 0,
            "bak"  : 0,
            "old"  : 0,
            "ppt"  : 0,
            "pptx" : 0,
            "accdb" : 0,
            "pdf"   : 0,
            "vbs"   : 0,
            "pl"    : 0,
            "sh"    : 0,
            "bat"   : 0,
            "sql"   : 0,
            "sqlite3" : 0,
            "xls"     : 0,
            "xlsm"    : 0,
            "xlsx"    : 0,
            "xltx"    : 0,
            "mdb"     : 0,
            "putty"   : 0,
            "ps"      : 0,
            "conf"    : 0,
            "config"  : 0,
            "ps"      : 0,
            "ashx"    : 0
        }

        self.payload = {
            "q"     : None,
            "start" : None
        }

    def _sleeper_( self ):
        """ sleep when needed """
        time = choice( [ x for x in range( self.config["minsleep"], self.config["maxsleep"] ) ] )
        sleep( time )

    def getlinks( self ):
        """ get files from google search """
        if self.config["agents"] is not None:
            agent = choice( [ x for x in open( self.config["agents"], "r" ).readlines() ] )
        else:
            agent = "Mozilla/11.0"
        self.headers["User-agent"] = agent
        for page in xrange( self.config["maxpage"] ):
            self.state["pagecount"] += 1
            self.payload["start"] = self.state["pagecount"] * 10
            for extension in list( self.filecounts ):
                print "[+] Searching for {}".format( extension )        
                try:
                    self.state["response"] = requests.get(
                        "https://www.google.ca/search?q=site:{}+filetype:{}&num=100".format( self.config["site"], extension ),
                        headers=self.headers
                    )
                    if "did not match any documents" in self.state["response"].text:
                        print "[-] No results for {}".format( extension )
                    soup = Soup( self.state["response"].text )
                    for h3 in soup.findAll( "h3", { "class" : "r" } ):
                        for a in h3.findAll( "a" ):
                            link = str( a )
                            self.url = re.search( r"(?P<url>https?://[^\s]+(?=\&amp;sa=U))", link )
                            if self.url:
                                self.state["links"].append( self.url.group( "url" ) )
                                self.filecounts[extension] += 1
                                print "[+] Result: {}".format( self.url.group( "url" ) )
                except Exception as E:
                    print "[!] Error: {}".format( E )
                    self._sleeper_()
                    self.state["pagecount"] -= 1
                print "[-] Sleeping before next request"
                self._sleeper_()
        print "[+] Done!!"

if __name__ == "__main__":
    google = Google( sys.argv[1], 3, 5, 1 )
    google.getlinks()
    for extension in list( google.filecounts ):
        print "[+] Found {} {}s".format( str( google.filecounts[extension] ), extension )
    with open( "links.txt", "w" ) as f:
        for link in google.state["links"]:
            f.write( "{}\n".format( link ) )
    f.close()
