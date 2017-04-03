#!/usr/bin/env python2

from random import choice
from time import sleep
from threading import Thread
from Queue import Queue

import os
import ssl
import socket
import argparse
import signal
import select
import sys

class HashKiller:

    def __init__( self, lpath, rpath, sendq, crackq, crack_log ):
        
        self.state = {
            "wordlists" : [ "{}/{}".format( lpath, x ).replace( "//", "/" ) for x in os.listdir( lpath ) ],
            "rules"     : [ "{}/{}".format( rpath, x ).replace( "//", "/" ) for x in os.listdir( rpath ) ],
            "sendq"     : sendq,
            "crackq"    : crackq,
            "crack_log" : crack_log
        }
        
    def crack( self, file_id, pwhash, mode ):
        outf = "{}.out".format( file_id )
        tmpf = "{}.tmp".format( file_id )
        hashf = "{}.hash".format( file_id )
        with open( hashf, "a" ) as hf:
            hf.write( "{}\n".format( pwhash ) )
        hf.close()
        
        if any( x in pwhash for x in [ "!@#$%^&*()_+=`~{}[];:'\"<>,./?|\\" ] ):
            data = {
                "style" : "error",
                "msg"   : "invalid hash"
            }
            self.state["sendq"].put( data )
            
        else:
            opts = "--remove --potfile-disable --gpu-temp-retain=83 --gpu-temp-abort=96 -d 1,2"
            chars = "'!@#$%^&*()1234567890'"
            args = []
            for wlist in self.state["wordlists"]:
                arg = "-a -0 -m {} {} -o {} {} {}".format( mode, opts, tmpf, hashf, wlist )
                args.append( arg )
            for wlist in self.state["wordlists"]:
                for rule in self.state["rules"]:
                    arg = "-a -0 -m {} {} -o {} -r {} {} {}".format( mode, opts, tmpf, rule, hashf, wlist )
                    args.append( arg )
            for mask in [ "?1", "?1?1", "?1?1?1", "?1?1?1?1" ]:
                arg = "-a 6 -m {} {} -o {} -1 {} {} {}".format( mode, opts, tmpf, chars, hashf, mask )
                args.append( arg )

            count = 0
            for arg in args:
                count += 1
                try:
                    data = {
                        "style" : "notice",
                        "msg"   : "running cycle {}/{} ...".format( 
                                        str( count ), 
                                        str( len( args ) )
                                  )
                    }
                    self.state["sendq"].put( data )
                    os.system( "hashcat {}".format( arg ) )
                    results = 0
                    for line in open( tmpf, "r" ):
                        if line:
                            results += 1
                            data = {
                                "style" : "good",
                                "msg"   : "{}:{}".format( pwhash, line.rstrip( "\n" ) )
                            }
                            self.state["sendq"].put( data )
                            with open( self.state["crack_log"], "a" ) as cl:
                                cl.write( data["msg"] )
                            cl.close()
                    if results > 0:
                        break
                except Exception as ERROR:
                    data = {
                        "style" : "alert",
                        "msg"   : "hashcat error for cycle {}/{}".format( str( count ), str( len( args ) ) )
                    }
                    self.state["sendq"].put( data )


    def check_for_hashes( self ):
        while True:
            if self.state["crackq"].empty() is not True:
                data = self.state["crackq"].get()
                pwhash = data["pwhash"]
                mode = data["mode"]
                file_id = data["file_id"]
                self.crack( file_id, pwhash, mode ) 
                self.state["crackq"].task_done()
            else:
                sleep( 5 )

class Core:

    def __init__( self, server, port, enable_ssl, nick, chan, lpath, rpath, crack_log ):
      
        self.config = {
            "server" : server,
            "port"   : int( port ),
            "enable_ssl" : enable_ssl,
            "nick" : nick,
            "chan" : chan
        }

        self.state = {
            "sock"      : socket.socket( socket.AF_INET, socket.SOCK_STREAM ),
            "connected" : False,
            "inchan"    : False,
            "sendq"     : Queue(),
            "crackq"    : Queue(),
            "crack_log" : crack_log,
            "ticker"    : 0
        }

        self.colours = {
            "good"   : "\x039",
            "notice" : "\x030",
            "alert"  : "\x038",
            "error"  : "\x034",
            "end"    : "\x03"
        }
        
        for i in range( 5 ):
            self.hashcat = HashKiller( lpath, rpath, self.state["sendq"], self.state["crackq"], self.state["crack_log"] )
            proc = Thread( target=self.hashcat.check_for_hashes )
            proc.daemon = True
            proc.start()

        self.state["sock"].connect(( self.config["server"], self.config["port"] ))
        if self.config["enable_ssl"] is True:
            self.state["sock"] = ssl.wrap_socket( self.state["sock"] )
        self.state["sock"].send( "USER {} {} {} :ohaio\n".format( self.config["nick"], self.config["nick"], self.config["nick"] ) )
        self.state["sock"].send( "NICK {}\n".format( self.config["nick"] ) )
        self.state["sock"].setblocking( 0 )
        buff = b""

        while True:
            
            lines = []

            if self.state["sendq"].empty() is not True and self.state["inchan"] is True:
                data = self.state["sendq"].get()
                self.send( data )
                self.state["ticker"] += 1
                self.state["sendq"].task_done()
            else:
                self.state["ticker"] += 1
            
            if ( self.state["ticker"] % 5000 == 0 ) and self.state["inchan"] is True:
                self.banner()
            
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
                        self.state["sock"].send( "JOIN {}\n".format( self.config["chan"] ) )
                        self.state["inchan"] = True

                    if "!crack" in line:
                        try:
                            msg = line.split( ":" )[2]
                            file_id = ""
                            while True:
                                file_id += choice( [ x for x in "abcdefghijklmnopqrstuvwxyz1234567890" ] )
                                if len( file_id ) == 10:
                                    break
                            data = {
                                "file_id" : file_id,
                                "mode"    : msg.split()[1],
                                "pwhash"  : msg.split()[2]
                            }
                            self.state["crackq"].put( data )
                            data = {
                                "style" : "notice",
                                "msg"   : "Queued as {} with job id: {}...".format( msg.split()[2], file_id ) 
                            }
                            self.state["sendq"].put( data )
                        except:
                            print "[!] Splitting error"


    def send( self, data ):
        formatted = "{}{}{}".format( self.colours[data["style"]], data["msg"], self.colours["end"] )
        self.state["sock"].send( "PRIVMSG {} :{}\n".format( self.config["chan"], formatted ) )

    
    def banner( self ):
        msg = "{}={}X{}= \x030Powered By Blackcatz {}={}X{}={}".format( 
                self.colours["good"],
                self.colours["alert"],
                self.colours["error"],
                self.colours["good"],
                self.colours["alert"],
                self.colours["error"],
                self.colours["end"]
        )
        self.state["sock"].send( "PRIVMSG {} :{}\n".format( self.config["chan"], msg ) )

if __name__ == "__main__":

    server = None
    port = None
    enable_ssl = None
    nick = None
    chan = None

    def signal_handler( signal, frame ):
        print "[!] Shutting down"
        sys.exit( 0 )

    parser = argparse.ArgumentParser( "crack hashes" )
    parser.add_argument( "-s", "--server", required=True, help="server to connect to" )
    parser.add_argument( "-p", "--port", required=True, help="port to connect to" )
    parser.add_argument( "-e", "--ssl", required=False, help="enable SSL", action="store_true" )
    parser.add_argument( "-n", "--nick", required=True, help="nick to identify with" )
    parser.add_argument( "-c", "--chan", required=True, help="chan to spam" )
    parser.add_argument( "-l", "--list_path", required=True, help="path to wordlists" )
    parser.add_argument( "-r", "--rule_path", required=True, help="path to rules" )
    parser.add_argument( "-a", "--crack_log", required=True, help="crack log to write to" )

    args = vars( parser.parse_args() )
    
    server = args["server"] if args["server"] else None
    port   = args["port"] if args["port"] else None
    enable_ssl = args["ssl"] if args["ssl"] else False
    nick = args["nick"] if args["nick"] else None
    chan = args["chan"] if args["chan"] else None
    lpath = args["list_path"] if args["list_path"] else None
    rpath = args["rule_path"] if args["rule_path"] else None
    crack_log = args["crack_log"] if args["crack_log"] else None

    signal.signal( signal.SIGINT, signal_handler )
    print "[+] Press Ctrl+C to quit"

    core = Core( server, port, enable_ssl, nick, chan, lpath, rpath, crack_log )
