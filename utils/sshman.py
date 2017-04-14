#!/usr/bin/env python2

"""
connect to a bunch of servers over ssh and get a shitty 
shell to exec commands on all of them at once
"""

from threading import Thread
from Queue import Queue
from time import sleep
import paramiko
import argparse

printq = Queue()
cmdq = Queue()
servers = []
sessions = []

class Session:
    def __init__( self, host, port, user, key, passwd, printq ):

        self.printq = printq
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        self.state = {
            "host"      : host,
            "user"      : user,
            "key"       : key,
            "passwd"    : passwd,
            "connected" : False
        }

        if key is not None:
            try:
                self.ssh.connect( host, port, username=user, key_filename=key)
                self.state["connected"] = True
            except Exception as ERROR:
                self.printq.put( "[!] Key authentication failed to host {}: {}".format( host, ERROR ) )

        elif passwd is not None:
            try:
                self.ssh.connect( host, port, username=user, password=passwd )
                self.state["connected"] = True
            except Exception as ERROR:
                self.printq.put( "[!] Passwd authentication failed to host {}: {}".format( host, ERROR ) )

        else:
            self.printq.put( "[!] No password/key specified, failed to connect to host {}".format( host ) )

    def exec_cmd( self, cmd ):
        if self.state["connected"] is True:
            if cmd == "exit":
                self.ssh.close()
            else:
                stdin, stdout, stderr = self.ssh.exec_command( cmd )
                for line in stdout.readlines():
                    self.printq.put( "[{}] {}".format( self.state["host"], line.rstrip( "\n" ) ) )

def session_manager():
    while True:
        if cmdq.empty() is not True:
            cmd_stub = cmdq.get()
            for session in sessions:
                if session.state["host"] == cmd_stub["host"]:
                    session.exec_cmd( cmd_stub["cmd"] )
                    break
            cmdq.task_done()
        else:
            sleep( 0.25 )

def printer():
    while True:
        if printq.empty() is not True:
            msg = printq.get()
            print msg
            printq.task_done()

if __name__ == "__main__":
    parser = argparse.ArgumentParser( "Manage multiple servers over SSH" )
    parser.add_argument( "--servers", "-s", required=True, help="list of servers to manage" )
    parser.add_argument( "--key", "-k", required=False, help="SSH key to use" )
    parser.add_argument( "--user", "-u", required=False, help="username to use" )
    parser.add_argument( "--passwd", "-p", required=False, help="password to use" )
    parser.add_argument( "--threads", "-t", required=False, help="threads to use" )
    parser.add_argument( "--port", "-P", required=False, help="port to connect to" )

    args = vars( parser.parse_args() )

    sfile = args["servers"] if args["servers"] else None
    key = args["key"] if args["key"] else None
    user = args["user"] if args["user"] else None
    passwd = args["passwd"] if args["passwd"] else None
    threads = int( args["threads"] ) if args["threads"] else 1
    port = int( args["port"] ) if args["port"] else 22

    if sfile is not None:
        for line in open( sfile, "r" ).readlines():
            servers.append( line.rstrip( "\n" ) )

    print "[+] Multi-SSH Shell"
    print "[>] Loading..."
    for host in servers:
        sessions.append( Session( host, port, user, key, passwd, printq ) )

    for i in range( threads ):
        proc = Thread( target=session_manager )
        proc.daemon = True
        proc.start()

    proc = Thread( target=printer )
    proc.daemon = True
    proc.start()

    print "[>] Connected to {} hosts".format( str( len( sessions ) ) )
    while True:
        sleep( 1 )
        cmd = raw_input( "[~] =>: " )
        cmd = cmd.lower()
        if cmd == "exit":
            printq.put( "[>] Exiting..." )
            for server in servers:
                cmd_stub = {
                    "host" : server,
                    "cmd"  : cmd
                }
                cmdq.put( cmd_stub )
            break
        elif len( cmd ) > 0:
            printq.put( "[>] Executing: {}".format( cmd ) )
            for server in servers:
                cmd_stub = {
                    "host" : server,
                    "cmd"  : cmd
                }
                cmdq.put( cmd_stub )
        else:
            pass
