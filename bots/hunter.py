#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
from multiprocessing import Process, Queue
from random import randint, choice
from time import sleep

import urllib2, re, sys, socket, ssl, signal, argparse

class Core:

    def __init__( self, server, port, enable_ssl, nick, chan ):
        
        self.config = {
            "server"     : server,
            "port"       : int( port ),
            "enable_ssl" : enable_ssl,
            "nick"       : nick,
            "chan"       : chan
        }

        self.state = {
            "sendq"   : Queue(),
            "procs"   : [],
            "proxies" : [],
            "socket"  : socket.socket( socket.AF_INET, socket.SOCK_STREAM ),
            "inchan"  : False
        }

        self.miners = {
            "pastebiner"    : self.pastebiner,
            "sprungebruter" : self.sprungebruter
            #"eightchanscan" : self.eightchanscan
        }

        self.stats = {
            "requests"  : 0,
            "email"     : 0,
            "emailpass" : 0,
            "link"      : 0,
            "ipv4"      : 0,
            "ipv4port"  : 0
        }

        self.agents = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        ]

        self.tracker = {
            "email"     : 0,
            "emailpass" : 0,
            "link"      : 0,
            "ipv4"      : 0,
            "ipv4port"  : 0,
        }
            
        self.visited = {
            "pastebin"  : [],
            "threads"   : []
        }

        self.regexes = {
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
            
    def _good_( self, msg ):
        formated = "\x039[+] {}\x03".format( msg )
        self.state["sendq"].put( formated )

    def _error_( self, msg ):
        formated = "\x034[!] {}\x03".format( msg )
        self.state["sendq"].put( formated )
    
    def _action_( self, msg ):
        formated = "\x032[*] {}\x03".format( msg )
        self.state["sendq"].put( formated )

    def _verb_( self, msg ):
        formated = "\x0315[>] {}\x03".format( msg )
        self.state["sendq"].put( formated )

    def _warn_( self, msg ):
        formated = "\x038[-] {}".format( msg )
        self.state["sendq"].put( formated )
    
    def _GET_( self, target_url ):
        """ HTTP GET request returns response """
        
        self.header = {
            "User-Agent"      : choice( self.agents ),
            "Accept"          : "text/html"
        }

        self.stats["requests"] += 1
        return urllib2.urlopen( urllib2.Request( target_url, headers=self.header ) )

    def _match_( self, target_url ):
        """ Check for goodies """
        try:
            for line in self._GET_( target_url ).readlines():
                for regex in self.regexes:
                    if re.search( self.regexes[regex], line ):
                        self.tracker[regex] += 1
                        self.stats[regex] += 1

            for i in self.tracker:
                if self.tracker[i] > 0:
                    msg = "Found {} {} in {}".format( self.tracker[i], i, target_url )
                    self._good_( msg )
            
            for i in self.tracker:
                self.tracker[i] = 0
        
        except Exception as ERROR:
            msg = "Match request error: {}".format( ERROR )
            self._error_( msg )

    def _checkpb_( self ):
        try:
            soup = Soup( self._GET_( "http://pastebin.com" ).read() )
            for menu in soup.findAll( "ul", { "class" : "right_menu" } ):
                for li in menu.findAll( "li" ):
                    for a in li.findAll( "a" ):
                        rawpaste = ( "http://pastebin.com/raw{}".format( a['href'] ) )
                        checked = False
                        for i in self.visited["pastebin"]:
                           if rawpaste in i:
                                checked = True
                        if checked is False:
                            self.visited["pastebin"].append( rawpaste )
                            self._action_( "Checking {}".format( rawpaste ) )
                            self._match_( rawpaste )
        except Exception as ERROR:
            msg = "PBMon threw an error: {}".format( ERROR )
            self._error_( msg )
            self._warn_( "Pausing PBMon for 300 seconds" )
            sleep( 297 )

    def _sprungebrute_( self ):
        nid = ""
        symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        while len( nid ) < 4:
            n = randint( 0, 35 )
            nid = nid + symbols[n:n + 1]
        try:
            sprunge_url = "http://sprunge.us/{}".format( nid )
            self._action_( "Trying {}".format( sprunge_url ) )
            self._match_( sprunge_url )
        except Exception as ERROR:
            msg = "SprungeBrute threw an error: {}".format( ERROR )
            self._error_( msg )
            self._warn_( "Pausing SprungeBruter for 60 seconds" )
            sleep( 58 )

    def _scan8chan_( self ):
        try: #currently im only interested in this board
            soup = Soup( self._GET_( "http://8ch.net/baphomet/catalog.html" ).read() )
            for thread in soup.findAll( "div", { "class" : "mix" } ):
                for href in thread.findAll( "a" ):
                    if "baphomet/res" in href['href'] and href['href'].endswith( "html" ):
                        thread_url = "http://8ch.net{}".format( href['href'] )
                        self._action_( "Lurking {}".format( thread_url ) )
                        self._match_( thread_url )
        except Exception as ERROR:
            msg = "8ChanScan threw an error: {}".format( ERROR )
            self._error_( msg )
            self._warn_( "Pausing 8ChanScan for 120 seconds" )
            sleep( 60 )

    def pastebiner( self ):
        while True:
            self._checkpb_()
            sleep( 3 )

    def sprungebruter( self ):
        while True:
            self._sprungebrute_()
            sleep( 2 )

    def eightchanscan( self ):
        while True:
            self._scan8chan_()
            sleep( 60 )

    def start_bot( self ):
        """ connect bot and start miners """
        self.state["socket"].settimeout( 2 )
        self.state["socket"].connect(( self.config["server"], self.config["port"] ))
        
        if self.config["enable_ssl"] is True:
            self.state["socket"] = ssl.wrap_socket( self.state["socket"] )
        
        self.state["socket"].send( "USER {} {} {} :ohaio\n".format(
            self.config["nick"], self.config["nick"], self.config["nick"]
        ))
        self.state["socket"].send( "NICK {}\n".format( self.config["nick"] ) )

        for i in self.miners:
            proc = Process( target=self.miners[i] )
            proc.start()
            self.state["procs"].append( proc )
            
        data = ""
        while True:
            try:
                data = self.state["socket"].recv( 2048 )
            except:
                pass
        
            if data.find( "PING :" ) != -1:
                self.state["socket"].send( "PONG :{}\n".format( data.split( ":" )[1] ) )
                if self.state["inchan"] is True:
                    self._verb_( "Runtime Statistics" )
                    for i in self.stats:
                        self._verb_( "{} => {}".format( i, self.stats[i] ) )
                continue

            elif "376" in data and self.state["inchan"] is False:
                self.state["socket"].send( "JOIN {}\n".format( self.config["chan"] ) )
                self.state["inchan"] = True

            if self.state["sendq"].empty() is not True and self.state["inchan"] is True:
                line = self.state["sendq"].get()
                msg = "PRIVMSG {} :{}\n".format( self.config["chan"], line )
                self.state["socket"].send( msg )
                print "[>>>] {}".format( msg.rstrip( "\n" ) )
        
            continue


if __name__ == "__main__":
    """ start bot and mine all the things """    
    server     = None
    port       = None
    enable_ssl = False
    nick       = None
    chan       = None

    def signal_handler( signal, frame ):
        print "[!] Shutting down"
        for proc in procs:
            proc.terminate()
        sys.exit( 0 )

    parser = argparse.ArgumentParser( "Hunt for goodies" )
    parser.add_argument( "-s", "--server", required=True, help="server to connect to" )
    parser.add_argument( "-p", "--port", required=True, help="port to connect to" )
    parser.add_argument( "-e", "--ssl", required=False, help="enable SSL", action="store_true" )
    parser.add_argument( "-n", "--nick", required=True, help="nick to identify with" )
    parser.add_argument( "-c", "--chan", required=True, help="chan to spam" )

    args = vars( parser.parse_args() )

    server = args["server"] if args["server"] else None
    port   = args["port"] if args["port"] else None
    enable_ssl = args["ssl"] if args["ssl"] else False
    nick = args["nick"] if args["nick"] else None
    chan = args["chan"] if args["chan"] else None

    signal.signal( signal.SIGINT, signal_handler )
    print "[+] Press Ctrl+C to quit"

    core = Core( server, port, enable_ssl, nick, chan )
    core.start_bot()
