#!/usr/bin/env python2
import socket
import sys

sock  = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
sock.connect(( sys.argv[1], 25 ))
        
while True:
    data = sock.recv( 4096 )
    print data
    if "ESMTP" in data: #data before sending EHLO
        sock.send( "EHLO lol.com\r\n" )
    if "250 CHUNKING" in data: #last line after EHLO
        sock.send( "MAIL FROM:<noone@gmail.com>\r\n" )
    if "250" and "Sender OK" in data:
        elem = 0
        emails = [ x for x in open( sys.argv[2], "r" ) ]
        for email in emails:
            """ check response for each email """
            while True:
                email = emails[elem].rstrip( "\n" ) if elem < len( emails ) else None
                if email is None:
                    break
                sock.send( "RCPT TO:<{}>\r\n".format( email ) )
                data = sock.recv( 4096 )
                if data is not None:
                    #print data
                    if "250" in data:
                        print "\033[1;32m[+]\033[1;m Valid: {}".format( email )
                    elif "550" in data:
                        print "\033[1;31m[!]\033[1;m Invalid: {}".format( email )
                    else:
                        pass
                elem += 1
                data = None
        break

sock.close()

