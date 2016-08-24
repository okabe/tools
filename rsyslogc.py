#/usr/bin/env python2

import socket
import argparse
import sys

class Rsyslog:

    def __init__( self, rhost, rport, facility, level ):
    
        self.facility = {
            "kern"    : 0,
            "user"    : 1,
            "mail"    : 2,
            "daemon"  : 3,
            "auth"    : 4,
            "syslog"  : 5,
            "lpr"     : 6,
            "news"    : 7,
            "uucp"    : 8,
            "cron"    : 9,
            "priv"    : 10,
            "ftp"     : 11,
            "ntp"     : 12,
            "audit"   : 13,
            "alert"   : 14,
            "local_0" : 16,
            "local_1" : 17,
            "local_2" : 18,
            "local_3" : 19,
            "local_4" : 20,
            "local_5" : 21,
            "local_6" : 22,
            "local_7" : 23
        }

        self.level = {
            "emergency" : 0,
            "alert"     : 1,
            "critical"  : 2,
            "error"     : 3,
            "warning"   : 4,
            "notice"    : 5,
            "verbose"   : 6,
            "debug"     : 7
        }

        self.state = {
            "rhost"    : rhost,
            "rport"    : int( rport ),
            "facility" : self.facility[facility],
            "level"    : self.level[level],
            "sock"     : socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        }
    
    def send( self, msg, level ):
        data = "<{}>{}".format( self.state["level"] + self.state["facility"] * 8, msg )
        self.state["sock"].sendto( data, ( self.state["rhost"], self.state["rport"] ) )

    def emergency( self, msg ):
        self.send( msg, self.level["emergency"] )

    def alert( self, msg ):
        self.send( msg, self.level["alert"] )

    def critical( self, msg ):
        self.send( msg, self.level["critical"] )

    def error( self, msg ):
        self.send( msg, self.level["error"] )

    def warning( self, msg ):
        self.send( msg, self.level["warning"] )

    def notice( self, msg ):
        self.send( msg, self.level["notice"] )

    def verbose( self, msg ):
        self.send( msg, self.level["verbose"] )

    def debug( self, msg ):
        self.send( msg, self.level["debug"] )

if __name__ == "__main__":


    parser = argparse.ArgumentParser( "Send data to rsyslog server" )
    parser.add_argument( "--rhost",    required=True, help="rsyslog host to send data to" )
    parser.add_argument( "--rport",    required=True, help="rsyslog port to send data to" )
    parser.add_argument( "--facility", required=True, help="RFC 5424 facility" )
    parser.add_argument( "--level",    required=True, help="RFC 5424 level" )
    parser.add_argument( "--msg",      required=True, help="data to send" )

    args = vars( parser.parse_args() )
    
    rhost    = args["rhost"] if args["rhost"] else None
    rport    = args["rport"] if args["rport"] else None
    facility = args["facility"] if args["facility"] else None
    level    = args["level"] if args["level"] else None
    msg      = args["msg"] if args["msg"] else None

    client = Rsyslog( rhost, rport, facility, level )
    if level == "emergency":
        client.emergency( msg )
    
    elif level == "alert":
        client.alert( msg )
    
    elif level == "critical":
        client.critical( msg )
    
    elif level == "error":
        client.error( msg )

    elif level == "warning":
        client.warning( msg )

    elif level == "notice":
        client.notice( msg )

    elif level == "verbose":
        client.verbose( msg )

    elif level == "debug":
        client.debug( msg )

    else:
        print "invalid message level"
        sys.exit()
        
    print "Sent {} message to {} facility on {}:{} -> {}".format( level, facility, rhost, rport, msg )
