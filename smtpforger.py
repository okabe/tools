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
        sock.send( "MAIL FROM:<administrator@{}>\r\n".format( sys.argv[2] ) )
    if "250" and "Sender OK" in data:
        sock.send( "RCPT TO:<administrator@{}>\r\n".format( sys.argv[2] ) )
    if "550" and "Access denied" in data:
        print "[!] Forged mail attempt failed"
    else:
        sock.send( "Data\r\n" )
        sock.send( "Subject: Hello world\nThe quick brown fox jumped over the lazy dog\n.\n" )
        print "[+] Forged mail was  appears to work"
sock.close()
