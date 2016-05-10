#!/usr/bin/env python2

""" dork google for linkedin profiles for a given 
company, filter out the false positives, then spider 
the profiles found to find more employees, generate 
a list and convert to emails based on a common naming 
convention """

from multiprocessing import Process, Queue
from BeautifulSoup import BeautifulSoup as Soup
from random import choice
from time import sleep

import socket
import signal
import re
import argparse
import sys
import urllib2
import requests

class Reporter:
    def __init__( self, msg, level ):
        """ based of RFC 5424 """
        self.config = {
            "msg"   : msg,
            "level" : level
        }
        
        self.status = {
            "emergency" : 0,
            "alert"     : 1,
            "critical"  : 2,
            "error"     : 3,
            "warning"   : 4,
            "notice"    : 5,
            "verbose"   : 6,
            "debug"     : 7,
            "good"      : 8 #this is not part of the RFC but w.e
        }

        self.colour = {
            0   : "\033[1m\033[41m", #white on red
            1   : "\033[91m", #red
            2   : "\033[1m\033[1;31;103m", #red on yellow
            3   : "\033[33m", #yellow
            4   : "\033[1m\033[45m", #white on magenta
            5   : "\033[95m", #magenta
            6   : "\033[1m\033[104m", #white on blue
            7   : "\033[96m", #cyan,
            8   : "\033[32m",
            "E" : "\033[0m" #end colour
        }

        self.symbol = {
            0 : "!!!",
            1 : "!!!",
            2 : "---",
            3 : "---",
            4 : "***",
            5 : "***",
            6 : "^^^",
            7 : "^^^",
            8 : "+++"
        }
        
        print "[{}{}{}] {}{}{} >>~> {}{}{}".format(
            self.colour[self.status[self.config["level"]]],
            self.symbol[self.status[self.config["level"]]],
            self.colour["E"],
            self.colour[self.status[self.config["level"]]],
            self.config["level"].upper(),
            self.colour["E"],
            self.colour[self.status[self.config["level"]]],
            self.config["msg"],
            self.colour["E"]
        )

class Google:
    """ scrape google search results """
    def __init__( self, org, agents, minsleep, maxsleep, maxpage, loglevel ):
        self.config = {
            "org"      : org,
            "agents"   : agents,
            "minsleep" : int( minsleep ),
            "maxsleep" : int( maxsleep ),
            "maxpage"  : int( maxpage ),
            "loglevel" : loglevel,
            "url"      : "https://www.google.ca/search?q=site:linkedin.com+-Top+-profiles+-jobs+-dir+-topic+works+at+"
        }

        self.state = {
            "proxy"     : None,
            "opener"    : None,
            "request"   : None,
            "response"  : None,
            "links"     : [],
            "pagecount" : 0
        } 
        
        self.headers = { 
            "User-agent" : None
        }

        self.payload = {
            "start" : None
        }

        if self.config["maxpage"] is None:
            self.config["maxpage"] = 10

    def getlinks( self ):
        """ get links from google search """
        if self.config["agents"] is not None:
            agent = choice( [ x for x in open( self.config["agents"], "r" ).readlines() ] )
        else:
            agent = "Mozilla/11.0"
        self.headers["User-agent"] = agent
        for page in xrange( self.config["maxpage"] ):
            self.state["pagecount"] += 1
            self.payload["start"] = self.state["pagecount"] * 10
            try:
                Reporter( "Trying page {}".format( str( self.state["pagecount"] ) ), "verbose" )
                self.config["url"] += self.config["org"].replace( " ", "+" ) 
                self.state["response"] = requests.get(
                    self.config["url"] + "&num=150",
                    headers=self.headers
                )
            except Exception as E:
                Reporter( E, "emergency" )
            try:
                if "CAPTCHA" in self.state["response"].text:
                    Reporter( "UH-OH we hit a CAPTCHA, sleeping before retrying request", "alert" )
                    self._sleeper_()
                    self.state["pagecount"] -= 1
                    self.getlinks()
                soup  = Soup( self.state["response"].text )
                for h3 in soup.findAll( "h3", { "class" : "r" } ):
                    for a in h3.findAll( "a" ):
                        link = str( a )
                        self.url = re.search( r"(?P<url>https?://[^\s]+(?=\&amp;sa=U))", link )
                        if self.url:
                            self.state["links"].append( self.url.group( "url" ) )
                            if self.config["loglevel"] <= 5:
                                Reporter( self.url.group( "url" ), "debug" )

            except Exception as E:
                Reporter( "Response was NoneType, sleeping before retry", "alert" )
                self._sleeper_()
                self.state["pagecount"] -= 1
            Reporter( "Sleeping before next page request", "verbose" )
            self._sleeper_()
        Reporter( "Done!!", "verbose" )

    def _sleeper_( self ):
        """ sleep between page requests """
        time = choice( [ x for x in range( self.config["minsleep"], self.config["maxsleep"] ) ] )
        if self.config["loglevel"] <= 4:
            Reporter( "sleeping for {}".format( str( time ) ), "notice" )
            sleep( time )

class Harvest:
    """ linkedin profiles are not always consistent with what tags are availible so we run a few 
    tests to determine if the given profile is something worth noting or not """
    def __init__( self, url, agent, org, loglevel ):
        self.config = {
            "url" : url,
            "org" : org
        }

        self.result = {
            "name"   : None,
            "status" : False,
        }

        self.state = {
            "opener"   : None,
            "request"  : None,
            "continue" : False
        }

        request_headers = { 
            "Host"            : "www.linkedin.com", 
            "User-Agent"      : agent, 
            "Accept"          : "text/html",
            "Accept-Language" : "en-US,en;q=0.5"
        }

        try:
            self.state["request"] = urllib2.Request( url, headers=request_headers )
            response = urllib2.urlopen( self.state["request"] )
            soup = Soup( response.read() )
            self.state["continue"] = True
            for profile in soup.findAll( "div", { "class" : "profile-overview-content" } ):
                if self.config["org"] in profile.text:
                    self.result["status"] = True
                    for h1 in profile.findAll( "h1", { "class" : "fn" } ):
                       self.result["name"] = h1.text #grab the name
        except Exception as E:
            Reporter( "Failed to request profile: {}".format( E ), "alert" )

        if loglevel > 5:
            Reporter( "scraped {}".format( url ), "verbose" )

class Master:
    """ this is where it all comes together """
    def __init__( self, organization, stub, agents, proxies, maxpage, maxsleep, minsleep, loglevel, output ):
        self.config = {
            "org"       : organization,
            "stub"      : stub,
            "agents"    : agents,
            "proxies"   : proxies,
            "maxpage"   : maxpage,
            "maxsleep"  : maxsleep,
            "minsleep"  : minsleep,
            "loglevel"  : loglevel,
            "output"    : output
        }
        
        self.state = {
            "links"   : Queue(),
            "names"   : Queue(),
            "emails"  : Queue(),
            "results" : [],
            "procs"   : [],
            "output"  : None
        }

        #launch our process queues
        email_generator     = Process( target=self._email_generator_ )
        profiler            = Process( target=self._profiler_ )
        dup_filter          = Process( target=self._dup_filter_ )
        self.state["procs"] = [ email_generator, profiler, dup_filter ]
        email_generator.start()
        profiler.start()
        dup_filter.start()

        #feed process queue google search results
        google = Google( org, agents, minsleep, maxsleep, maxpage, loglevel )
        google.getlinks() #ideally you would background this, but for now its fine
        for i in google.state["links"]:
            self.state["links"].put( i )
        
        if self.config["output"] is not None:
            self.state["output"] = open( self.config["output"], "w" )

    def _email_generator_( self ):
        while True: #wait for queue to populate
            """ generate an email based off a naming convention """
            if self.state["names"].empty() is not True:
                try:
                    name = self.state["names"].get()
                    FN   = name.split( " " )[0].lower()
                    LN   = name.split( " " )[1].lower()
                    FI   = FN[0]
                    LI   = LN[0]
                    stub = self.config["stub"]
                    if "|FN|" in self.config["stub"]:
                        stub = stub.replace( "|FN|", FN )
                    if "|LN|" in self.config["stub"]:
                        stub = stub.replace( "|LN|", LN )
                    if "|FI|" in self.config["stub"]:
                        stub = stub.replace( "|FI|", FI )
                    if "|LI|" in self.config["stub"]:
                        stub = stub.replace( "|LI|", LI )
                    """ send to email queue for filtering """
                    self.state["emails"].put( stub )
                    #Reporter( "Generated Email: {}".format( stub ), "verbose" )
                except Exception as E:
                    Reporter( E, "alert" )
            else: #continue to wait
                sleep( 0.25 )
                continue

    def _run_harvest_( self ):
        logname = False 
        profile = self.state["links"].get()
        agent   = choice( [ x for x in open( self.config["agents"], "r" ).readlines() ] )
        Reporter( "Crawling {}".format( profile ), "verbose" )
        harvest = Harvest( profile, agent, self.config["org"], self.config["loglevel"] )
        if harvest.result["status"] is True:
            #Reporter( "Found name: {}".format( harvest.result["name"] ), "debug" )
            self.state["names"].put( harvest.result["name"] )

    def _profiler_( self ):
        while True: #wait for queue to populate
            """ visit a linkedin profile and pull out the name """
            if self.state["links"].empty() is not True:
                self._run_harvest_() 
                sleep( 3 ) #throttle so linkedin doesnt throw a 999 at us
            else: #wait for queue to populate
                sleep( 0.25 )
                continue

    def _dup_filter_( self ):
        while True: #wait for queue to populate
            """ filter out duplicates emails """
            if self.state["emails"].empty() is not True:
                email = self.state["emails"].get()
                if email not in self.state["results"]:
                    self.state["results"].append( email )
                    Reporter( email, "good" )
                    if self.state["output"] is not None:
                        self.state["output"].write( "{}\n".format( email ) )
                else: #its a duplicate so ignore
                    pass
            else: #wait for queue to populate
                sleep( 0.25 )
                continue

if __name__ == "__main__":
    """ create our entry point, declare our globals and parse options """
    def help_msg():
        print """
 Options:
    --org <org>              : organization to hunt for
    --stub <stub>            : email generation stub, see --stub-help for detail
    --agents <agents.txt>    : list of useragents to spoof
    --proxies <proxies.txt>  : list of http proxies to scrape with
    --max_page <n>           : maximum number of google pages to scrape
    --max_sleep <n>          : maximum sleep time between google searches
    --min_sleep <n>          : minimum sleep time between google searches
    --log_level <n>          : verbosity on a scale of 1-7 as per RFC 5424
    --output <file.txt>      : log findings to a file
    --help                   : print this message
    --stub_help              : lrn2stub
"""
        sys.exit()

    def stub_help_msg():
        print """
Naming Convetion rules:
    first initial = FI
    first name    = FN
    last initial  = LI
    last name     = LN

Example 1: if the name John Doe is found
    --stub "|FN|_|LN|@companyxyz.com"
             |    |
             |     `substitute with "Doe"
              `substitue with "John"
    result = "john_doe@companyxyz.com"

Example 2:            
    --stub "|FI||LN|@companyxyz.com" 
             |   |
             |    `substitue with "Doe"
              `substitute with "J"
    result = "jdoe@companyxyz.com"
"""
        sys.exit()

    def signal_handler( signal, frame ):
        sys.exit() #an hero
                
    master = None
    parser = argparse.ArgumentParser( "Hunt for linkedin", add_help=False, usage="lihunter.py --help" )
    parser.add_argument( "--org" )
    parser.add_argument( "--stub" )
    parser.add_argument( "--agents" )
    parser.add_argument( "--proxies" )
    parser.add_argument( "--max_page" )
    parser.add_argument( "--max_sleep" )
    parser.add_argument( "--min_sleep" )
    parser.add_argument( "--log_level" )
    parser.add_argument( "--output" )
    parser.add_argument( "--help",      action="store_true" )
    parser.add_argument( "--stub_help", action="store_true" )

    args = vars( parser.parse_args() )
    
    if args["help"] is True:
        help_msg()

    if args["stub_help"] is True:
        stub_help_msg()

    #parse our options or set defaults
    org      = args["org"] if args["org"] else None
    stub     = args["stub"] if args["stub"] else None
    agents   = args["agents"] if args["agents"] else None
    proxies  = args["proxies"] if args["proxies"] else None
    maxpage  = args["max_page"] if args["max_page"] else 500
    maxsleep = args["max_sleep"] if args["max_sleep"] else 8
    minsleep = args["min_sleep"] if args["min_sleep"] else 3
    loglevel = args["log_level"] if args["log_level"] else 0
    output   = args["output"] if args["output"] else None

    if org is None or stub is None or agents is None:
        Reporter( "invalid switches", "emergency" )
        help_msg()

    else: #ready to rage
        signal.signal( signal.SIGINT, signal_handler )
        master = Master( org, stub, agents, proxies, maxpage, maxsleep, minsleep, loglevel, output )
