#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
from multiprocessing import Process, Queue
from threading import Thread
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
            "sendq"      : Queue(),
            "proxyq"     : Queue(),
            "emailpassq" : Queue(),
            "procs"      : [],
            "proxies"    : [],
            "emailpass"  : [],
            "link"       : [],
            "ipv4"       : [],
            "ipv4port"   : [],
            "socket"     : socket.socket( socket.AF_INET, socket.SOCK_STREAM ),
            "inchan"     : False
        }

        self.miners = {
            "pastebiner"    : self.pastebiner,
            "ghostbiner"    : self.ghostbiner,
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

    def _coming_soon_( self, msg ):
        formated = "\x0311[*] {}\x03".format( msg )
        self.state["sendq"].put( formated )

    def _verb_( self, msg ):
        formated = "\x030[>] {}\x03".format( msg )
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
        tmp = []
        for line in self._GET_( target_url ).readlines():
            for regex in self.regexes:
                if re.search( self.regexes[regex], line ):
                    self.tracker[regex] += 1
                    self.stats[regex] += 1
                    tmp.append( line.rstrip( "\n" ) )

        for i in self.tracker:
            if self.tracker[i] > 0:
                msg = "Found {} {} in {}".format( self.tracker[i], i, target_url )
                self._good_( msg )
                if "ipv4port" in i:
                    self._action_( "Checking {} for proxies".format( target_url ) )
                    for proxy in tmp:
                       self.state["proxyq"].put( proxy )
                elif "emailpass" in i:
                    #self._action_( "Checking {} for valid credentials".format( target_url ) )
                    self._coming_soon_( "Credential scanner coming soon!!!" )
                    for emailpass in tmp:
                        self.state["emailpassq"].put( emailpass )
            
        for i in self.tracker:
            self.tracker[i] = 0
        
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
                            self._match_( rawpaste )
        except Exception as ERROR:
            msg = "PBMon threw an error: {}".format( ERROR )
            self._error_( msg )
            self._warn_( "Pausing PBMon for 300 seconds" )
            sleep( 297 )

    def _checkgb_( self ):
        nid = ""
        symbols = "abcdefghijklmnopqrstuvwxyz0123456789"
        while len( nid ) < 5:
            nid = nid + choice( [ x for x in symbols ] )
        try:
            ghost_url = "https://ghostbin.com/paste/{}".format( nid )
            self._match_( ghost_url )
        except Exception as ERROR:
            msg = "GBMon threw and error : {}".format( ERROR )
            if "420" in msg:
                self._error_( msg )
                self._warn_( "Request was blocked!! Pausing GBMon for 24 hours" )
                sleep( ( 60 * 60 * 24 ) )
            pass

    def _sprungebrute_( self ):
        nid = ""
        symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        while len( nid ) < 4:
            n = randint( 0, 35 )
            nid = nid + symbols[n:n + 1]
        try:
            sprunge_url = "http://sprunge.us/{}".format( nid )
            #self._action_( "Trying {}".format( sprunge_url ) )
            self._match_( sprunge_url )
        except Exception as ERROR:
            msg = "SprungeBrute threw an error: {}".format( ERROR )
            self._error_( msg )
            self._warn_( "Service is down!! Pausing SprungeBrute for 24 hours" )
            sleep( ( 60 * 60 * 24 ) )

    def _scan8chan_( self ):
        try: #currently im only interested in this board
            soup = Soup( self._GET_( "http://8ch.net/baphomet/catalog.html" ).read() )
            for thread in soup.findAll( "div", { "class" : "mix" } ):
                for href in thread.findAll( "a" ):
                    if "baphomet/res" in href['href'] and href['href'].endswith( "html" ):
                        thread_url = "http://8ch.net{}".format( href['href'] )
                        #self._action_( "Lurking {}".format( thread_url ) )
                        self._match_( thread_url )
        except Exception as ERROR:
            msg = "8ChanScan threw an error: {}".format( ERROR )
            self._error_( msg )
            self._warn_( "Pausing 8ChanScan for 120 seconds" )
            sleep( 60 )

    def proxy_checker( self ):
        while True:
            if self.state["proxyq"] is not True:
                proxy = self.state["proxyq"].get().rstrip( "\n\r" )
                try:
                    opener = urllib2.build_opener( urllib2.ProxyHandler( { "http" : proxy } ) )
                    urllib2.install_opener( opener )
                    for i in urllib2.urlopen( "http://icanhazip.com/", timeout=2 ).readlines():
                        print "[+] Working proxy: {}".format( proxy )
                        self.state["proxies"].append( proxy )
                except Exception as E:
                    pass
            sleep( 1 )
            continue

    def asset_count( self, asset ):
        if len( self.state[asset] ) > 0:
            self.state[asset] = list( set( self.state[asset] ) )
            assetcount = str( len( self.state[asset] ) )
            self._verb_( " > {} {}".format( assetcount, asset ) )
        
    def pastebiner( self ):
        while True:
            self._checkpb_()
            sleep( 3 )

    def ghostbiner( self ):
        while True:
            self._checkgb_()
            sleep( 60 )

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
    
        for i in xrange( 18 ):
            proc = Thread( target=self.proxy_checker )
            proc.start()

        data   = ""
        ticker = 0
        while True:
            if ( ticker % 50 == 0 ) and self.state["inchan"] is True:
                self._verb_( ">> Data Hunter version 0.0.1 <<" )
                self._verb_( "=> Harvested" )
                
                if len( self.state["proxies"] ) > 0:
                    self.asset_count( "proxies" )

                if len( self.state["emailpass"] ) > 0:
                    self.asset_count( "emailpass" )

            try:
                data = self.state["socket"].recv( 2048 )
                print data
            except:
                pass
        
            if data.find( "PING :" ) != -1:
                self.state["socket"].send( "PONG :{}\n".format( data.split( ":" )[1] ) )
                continue

            elif "376" in data and self.state["inchan"] is False:
                self.state["socket"].send( "JOIN {}\n".format( self.config["chan"] ) )
                self.state["inchan"] = True

            if self.state["sendq"].empty() is not True and self.state["inchan"] is True:
                line = self.state["sendq"].get()
                msg = "PRIVMSG {} :{}\n".format( self.config["chan"], line )
                self.state["socket"].send( msg )
                print ">>> {}".format( msg.rstrip( "\n" ) )
                ticker += 1

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
