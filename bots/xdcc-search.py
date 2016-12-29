#!/usr/bin/env python2

"""
  this is source of the Blackcatz XDCC search bot, it was written very quickly as to help some user find some files... 
  so its hardly production ready. but it does work none the less.
  
  simple to use, ive named my iroffers based off the category of files they serve up, so just make a text file for the
  bot to use called packs.txt or something, with line by line name of categories.
  
  the bot then reads this and looks for the packlists in the current working directory, it then reads the lists into memory
  using the appropriate Pack object. 
  
  like i said this is not very well put together, and i will be updating sooner or later.
"""

from threading import Thread
from Queue import Queue
from time import sleep
import socket
import os
import argparse
import ssl
import select

class Pack:

    def __init__( self, category ):
        self.category = category
        self.files = {}

class Core:

    def __init__( self, server, port, enable_ssl, nick, chan, packs ):
        
        self.config = {
            "server"     : server,
            "port"       : int( port ),
            "enable_ssl" : enable_ssl,
            "nick"       : nick,
            "chan"       : "#blackcatz",
            "packs"      : packs
        }

        self.state = {
            "sock" : socket.socket( socket.AF_INET, socket.SOCK_STREAM ),
            "connected" : False,
            "inchan"    : False,
            "sendq"     : Queue(),
            "searchq"   : Queue(),
            "ticker"    : 0,
            "searchers" : []
        }

        for i in xrange( 4 ):
            proc = Thread( target=self.searcher )
            proc.daemon = True
            self.state["searchers"].append( proc )
            proc.start()

        self.packs = []

        with open( self.config["packs"], "r" ) as packconfig:
            self.packs = [ Pack( line.rstrip( "\n" ) ) for line in packconfig.readlines() ]
        packconfig.close()

        self.packer()

        self.state["sock"].connect(( self.config["server"], self.config["port"] ))
        if self.config["enable_ssl"] is True:
            self.state["sock"] = ssl.wrap_socket( self.state["sock"] )
        
        self.msgs = [
            "USER {} {} {} :ohaio\n".format( 
                self.config["nick"], self.config["nick"], self.config["nick"] ),
            "NICK {}\n".format(
                self.config["nick"] )
        ]
        
        for msg in self.msgs:
            self.state["sock"].send( msg )
        
        self.state["sock"].setblocking( 0 )

        buff = b""
        while True:
            
            lines = []
            self.state["ticker"] += 1

            if self.state["sendq"].empty() is not True and self.state["inchan"] is True:
                data = self.state["sendq"].get()
                self.send( data )
                self.state["sendq"].task_done()

            if ( self.state["ticker"] % 500 == 0 ) and self.state["inchan"] is True:
                self.state["sendq"].put( "checking for new packs..." )
                self.packer()

            ready = select.select( [self.state["sock"]], [], [], 1 )
            if ready[0]:
                try:
                    raw = self.state["sock"].recv( 512 )
                    buff = buff + raw
                    lines = buff.split( "\n" )
                    buff = lines.pop()
                except:
                    pass

            if len( lines ) > 0:
                for line in lines:

                    print line

                    if line.find( "PING :" ) != -1:
                        self.state["sock"].send( "PONG :{}\n".format( line.split( ":" )[1] ) )

                    if "376" in line and self.state["inchan"] is False:
                        self.state["sock"].send( "JOIN #blackcatz\n" )
                        self.state["inchan"] = True

                    if "PRIVMSG" in line and "#blackcatz" in line:
                        if line.split( ":" )[2].startswith( "!" ):
                            keyword = "".join( line.split( ":" )[2].split()[1:] )
                            self.state["searchq"].put( keyword )
                            self.state["sendq"].put( "Queued search for {}".format( keyword ) )

    def send( self, data ):
        self.state["sock"].send( "PRIVMSG {} :{}\n".format( self.config["chan"], data ) )

    def packer( self ):
        for f in os.listdir( "." ):
            if f.endswith( "txt" ):
                for pack in self.packs:
                    if pack.category in f:
                        print "[+] Adding from {}".format( f )
                        with open( "{}".format( f ), "r" ) as packlist:
                            for line in packlist:
                                if line.startswith( "#" ):
                                    packnumber = line.split()[0]
                                    packtitle  = " ".join( line.split()[3:] )
                                    pack.files[packtitle] = packnumber
                                    print " - {}:{}".format( packnumber, packtitle )
                        packlist.close()

    def _search( self, keyword ):
        found_something = False
        for pack in self.packs:
            for fn in pack.files:
                if keyword.lower() in fn.lower():
                    msg = "{}: {} - {}".format( pack.category, fn, pack.files[fn] )
                    self.state["sendq"].put( msg )
                    found_something = True
        return found_something
    
    def searcher( self ):
        while True:
            if self.state["searchq"].empty() is not True:
                keyword = self.state["searchq"].get()
                if self._search( keyword ) is False:
                    self.state["sendq"].put( "No results found" )
            else:
                sleep( 0.25 )


if __name__ == "__main__":
    
    server     = None
    port       = None
    enable_ssl = False
    nick       = None
    chan       = None
    packs      = None

    parser = argparse.ArgumentParser( "xdcc search bot" )
    parser.add_argument( "-s", "--server", required=True, help="irc server" )
    parser.add_argument( "-p", "--port", required=True, help="irc port" )
    parser.add_argument( "-e", "--enablessl", required=True, help="use ssl", action="store_true" )
    parser.add_argument( "-n", "--nick", required=True, help="nick to use" )
    parser.add_argument( "-c", "--chan", required=True, help="chan to join" )
    parser.add_argument( "-l", "--packlist", required=True, help="packs to search from" )

    args = vars( parser.parse_args() )

    server = args["server"] if args["server"] else None
    port = args["port"] if args["port"] else None
    enable_ssl = True if args["enablessl"] else False
    nick = args["nick"] if args["nick"] else None
    packs = args["packlist"] if args["packlist"] else None

    core = Core( server, port, enable_ssl, nick, chan, packs )
