#!/usr/bin/env python2

import socket
import sys

sock  = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
sock.connect(( sys.argv[1], 25 ))
        
while True:
    data = sock.recv( 4096 )
    if "ESMTP" in data: #data before sending EHLO
        sock.send( "EHLO lol.com\r\n" )
    if "250 " in data: #last line after EHLO
        sock.send( "MAIL FROM:<noone@gmail.com>\r\n" )
    if "250" and "Sender OK" in data:
        sock.send( "RCPT TO:<someone@gmail.com>\r\n" )
    if "550" and "Access denied" in data:
        print "[!] Relay attempt failed"
    else:
        print "[+] Relay appears to work"
sock.close()
