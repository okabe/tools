#!/usr/bin/env python2

"""

    use this at your own risk, i will not take responsibility for your actions (does a statement like this even mean anything?)

    this script is just for proof of concept !!! thanks to nergal for the idea of seeding searches with random wikipedia pages. the workflow is
    grab some random title from a wikipedia page, then google search it in some random country and fuzz each site that is returned... that being 
    said, i have not included any fuzzing in this script because thats probabbly frowned upon and illegal. but dorking is not sooo here it is :) 

"""

from BeautifulSoup import BeautifulSoup as Soup
from random import choice
from time import sleep
from threading import Thread
from Queue import Queue

import re
import requests
import ssl
import socket
import argparse
import signal
import select
import sys

class Dorker:
    
    def __init__( self, sendq ):
        self.state = {
            "sendq" : sendq,
            "wiki"  : "https://en.wikipedia.org/wiki/Special:Random"
        }
        
        self.agents = [
            "Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.0.1) Gecko/2008072820 Firefox/3.0.1 FirePHP/0.1.1.2",
            "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1.13) Gecko/20080313 SeaMonkey/1.1.9",
            "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; fr) AppleWebKit/412.7 (KHTML, like Gecko) Safari/412.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.3) Gecko/20030313",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.2.1) Gecko/20030409 Debian/1.2.1-9woody2",
            "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; fr) AppleWebKit/418.9.1 (KHTML, like Gecko) Safari/419.3",
            "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:15.0) Gecko/20120819 Firefox/15.0-x64 PaleMoon/15.0-x64",
            "Mozilla/5.0 (Windows NT 5.1; rv:12.3) Gecko/20120728 Firefox/12.3r2 PaleMoon/12.3r2",
            "Opera/9.21 (Windows NT 5.1; U; pl)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; de-DE; rv:0.9.4.1) Gecko/20020508 Netscape6/6.2.3",
            "Opera/9.52 (X11; Linux i686; U; fr)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2) Gecko/20070225 lolifox/0.32",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/533.2 (KHTML, like Gecko) Chrome/5.0.343.0 Safari/533.2",
            "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/418.8 (KHTML, like Gecko) NetNewsWire/2.1.1",
            "Mozilla/5.0 (compatible; Konqueror/4.1; DragonFly) KHTML/4.1.4 (like Gecko)",
            "Opera/9.23 (Windows NT 6.0; U; de)",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/4.0.222.4 Safari/532.2",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.8) Gecko/20071018 Firefox/2.0.0.8 Flock/1.0RC3",
            "Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; de-AT; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4"
        ]

        self.countries = {
            "afghanistan" : "google.com.af",
            "albania" : "google.al",
            "algeria" : "google.dz",
            "american samoa" : "google.as",
            "andorra" : "google.ad",
            "angola" : "google.it.ao",
            "anguila" : "google.com.ai",
            "antigua & barbuda" : "google.com.ag",
            "argentina" : "google.com.ar",
            "armenia" : "google.am",
            "ascension island" : "google.ac",
            "australia" : "google.com.au",
            "austria" : "google.at",
            "azerbaijan" : "google.az",
            "bahamas" : "google.bs",
            "bahrain" : "google.com.bh",
            "bangladesh" : "google.com.bd",
            "belarus" : "google.com.by",
            "belgium" : "google.be",
            "belize" : "google.com.bz",
            "benin" : "google.bj",
            "bhutan" : "google.bt",
            "bolivia" : "google.com.bo",
            "bosnia & herzegovinia" : "google.ba",
            "botswana" : "google.co.bw",
            "brazil" : "google.com.br",
            "british virgin islands" : "google.vg",
            "brunei" : "google.com.bn",
            "bulgaria" : "google.bg",
            "burkina faso" : "google.bf",
            "burundi" : "google.bi",
            "cambodia" : "google.com.kh",
            "cameroon" : "google.cm",
            "canada" : "google.ca",
            "cape verde" : "google.cv",
            "catalan countries" : "google.cat",
            "central african republic" : "google.cf",
            "chad" : "google.td",
            "chile" : "google.cl",
            "china" : "google.cn",
            "columbia" : "google.com.co",
            "congo, democratic republic" : "google.cd",
            "congo" : "google.cg",
            "cook islands" : "google.co.ck",
            "costa rica" : "google.co.cr",
            "cote d'ivoire" : "google.ci",
            "croatia" : "google.hr",
            "cuba" : "google.com.cu",
            "cyprus" : "google.com.cy",
            "czech republic" : "google.cz",
            "denmark" : "google.dk",
            "djibouti" : "google.dj",
            "dominica" : "google.dm",
            "dominican republic" : "google.com.do",
            "ecuador" : "google.com.ec",
            "egypt" : "google.com.eg",
            "el salvador" : "google.com.sv",
            "estonia" : "google.ee",
            "ethiopia" : "google.com.et",        
            "fiji" : "google.com.fj",
            "finland" : "google.fi",        
            "france" : "google.fr",
            "gabon" : "google.ga",
            "gambia" : "google.gm",
            "georgia" : "google.ge",
            "germany" : "google.de",
            "ghana" : "google.com.gh",
            "gibraltar" : "google.com.gi",
            "greece" : "google.gr",
            "greenland" : "google.gl",
            "guadeloupe" : "google.gp",
            "guatemala" : "google.com.gt",
            "guernsey" : "google.gg",
            "guyana" : "google.gy",
            "haiti" : "google.ht",
            "honduras" : "google.hn",
            "hong kong" : "google.com.hk",
            "hungary" : "google.hu",
            "iceland" : "google.is",
            "india" : "google.co.in",
            "indonesia" : "google.co.id",
            "iraq" : "google.iq",
            "ireland" : "google.ie",
            "isle of man" : "google.co.im",
            "israel" : "google.co.il",
            "italy" : "google.it",
            "ivory coast" : "google.ci",
            "jamaica" : "google.com.jm",
            "japan" : "google.co.jp",
            "jersey" : "google.co.je",
            "jordon" : "google.jo",
            "kazakhstan" : "google.kz",
            "kenya" : "google.co.ke",
            "kiribati" : "google.ki",
            "kuwait" : "google.com.kw",
            "kyrgyzstan" : "google.com.kg",
            "laos" : "google.la",
            "latvia" : "google.lv",
            "lebanon" : "google.com.lb",
            "lesotho" : "google.co.ls",
            "libya" : "google.com.ly",
            "liechtenstein" : "google.li",
            "lithuania" : "google.lt",
            "luxembourg" : "google.lu",
            "macedonia" : "google.mk",
            "madagascar" : "google.mg",
            "malawi" : "google.mw",
            "malaysia" : "google.com.my",
            "maldives" : "google.mv",
            "mali" : "google.ml",
            "malta" : "google.com.mt",
            "mauritius" : "google.mu",
            "mexico" : "google.com.mx",
            "micronesia" : "google.fm",
            "moldavia" : "google.md",
            "mongolia" : "google.mn",
            "montenegro" : "google.me",
            "montserrat" : "google.ms",
            "morocco" : "google.co.ma",
            "mozambique" : "google.co.mz",
            "namibia" : "google.com.na",
            "nauru" : "google.nr",
            "nepal" : "google.com.np",
            "netherlands" : "google.nl",
            "new zealand" : "google.co.nz",
            "nicaragua" : "google.com.ni",
            "niger" : "google.ne",
            "nigeria" : "google.com.ng",
            "niue" : "google.nu",
            "norfolk island" : "google.com.nf",
            "norway" : "google.no",
            "oman" : "google.com.om",
            "pakistan" : "google.com.pk",
            "palestine" : "google.ps",
            "panama" : "google.com.pa",
            "papua new guina" : "google.com.pg",
            "paraguay" : "google.com.py",
            "peru" : "google.com.pe",
            "philippines" : "google.com.ph",
            "pitcairn" : "google.pn",
            "poland" : "google.pl",
            "portugal" : "google.pt",
            "puerto rico" : "google.com.pr",
            "quatar" : "google.com.qa",
            "romania" : "google.ro",
            "russia" : "google.ru",
            "rwanda" : "google.rw",
            "saint helena" : "google.sh",
            "samoa" : "google.ws",
            "san marino" : "google.sm",
            "sao tome and principe" : "google.st",
            "saudia arabia" : "google.com.sa",
            "senegal" : "google.sn",
            "serbia" : "google.rs",
            "seychelles" : "google.sc",
            "sierra leone" : "google.com.sl",
            "singapore" : "google.com.sg",
            "slovakia" : "google.sk",
            "slovenia" : "google.si",
            "solomon islands" : "google.com.sb",
            "somalia" : "google.so",
            "south africa" : "google.co.za",
            "south korea" : "google.co.kr",
            "spain" : "google.es",
            "sri lanka" : "google.lk",
            "st vincent & grenadines" : "google.com.vc",
            "suriname" : "google.sr",
            "sweden" : "google.se",
            "switzerland" : "google.ch",
            "taiwan" : "google.com.tw",
            "tajikistan" : "google.com.tj",
            "tanzania" : "google.co.tz",
            "thailand" : "google.co.th",
            "timor-leste" : "google.tl",
            "togo" : "google.tg",
            "tokelau" : "google.tk",
            "tonga" : "google.to",
            "trinidad & tobago" : "google.tt",
            "tunisia" : "google.tn",
            "turkey" : "google.com.tr",
            "turkmenistan" : "google.tm",
            "uganda" : "google.co.ug",
            "ukraine" : "google.com.ua",
            "united arab emirates" : "google.ae",
            "united kingdom" : "google.co.uk",
            "united states" : "google.com",
            "uruguay" : "google.com.uy",
            "uzbekistan" : "google.co.uz",
            "vanuatu" : "google.vu",
            "venezuela" : "google.co.ve",
            "vietnam" : "google.com.vn",
            "virgin islands (us)" : "google.co.vi",
            "zambia" : "google.co.zm",
            "zimbabwe" : "google.co.zw"
        }

    def getwikitext( self ):
        try:
            soup = Soup( requests.get( self.state["wiki"] ).text )
            return soup.findAll( "h1", { "class" : "firstHeading" } )[0].text.encode( "ascii" )
        except Exception as unicode_error:
            return None

    def getlinks( self ):
        response = None
        google = choice( [ x for x in self.countries ] )
        while True:
            wikitext = self.getwikitext()
            if wikitext is not None:
                break
        randomheader = {
            "User-agent" : choice( self.agents )
        }
        data = {
            "style" : "notice",
            "msg"   : "checking {} for sites related to {}".format( google, wikitext )
        }
        self.state["sendq"].put( data )
        url = "https://{}/search?q={}&num=100".format( self.countries[google], wikitext.replace( " ", "+" ) )
        try:
            response = requests.get( url, headers=randomheader )
        except Exception as ERROR:
            data = {
                "style" : "error",
                "msg"   : "google search failed: {}".format( ERROR )
            }
            self.state["sendq"].put( data )

        if response is not None:

            try:
                if "CAPTCHA" in response.text:
                    data = {
                        "style" : "alert",
                        "msg"   : "hit a captcha, sleeping for 60 seconds before continuing"
                    }
                    self.state["sendq"].put( data )
                    sleep( 61 )
                else:
                    soup = Soup( response.text )
                    for h3 in soup.findAll( "h3", { "class" : "r" } ):
                        for a in h3.findAll( "a" ):
                            link = re.search( r"(?P<url>https?://[^\s]+(?=\&amp;sa=U))", str( a ) )
                            if link:
                                target = link.group( "url" )
                                if "wiki" in target:
                                    pass
                                else:
                                    data = {
                                        "style" : "notice",
                                        "msg"   : "checking {}".format( target )
                                    }
                                    self.state["sendq"].put( data )

                                ######################################
                                # put in some fuzzing functions here #
                                ######################################

            except Exception as ERROR:
                data = {
                    "style" : "error",
                    "msg"   : "something broke: {}".format( ERROR )
                }
                self.state["sendq"].put( data )


class Core:

    def __init__( self, server, port, enable_ssl, nick, chan ):
      
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
            "dorkproc"  : None,
            "ticker"    : 0
        }

        self.colours = {
            "good"   : "\x039",
            "notice" : "\x030",
            "alert"  : "\x038",
            "error"  : "\x034",
            "end"    : "\x03"
        }

        self.dorker = Dorker( self.state["sendq"] )
        self.state["dorkproc"] = Thread( target=self.scanner )
        self.state["dorkproc"].daemon = True
        self.state["dorkproc"].start()

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
            
            if ( self.state["ticker"] % 100 == 0 ) and self.state["inchan"] is True:
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

                    if line.find( "PING :" ) != -1:
                        self.state["sock"].send( "PONG :{}\n".format( line.split( ":" )[1] ) )

                    if "376" in line and self.state["inchan"] is False:
                        self.state["sock"].send( "JOIN {}\n".format( self.config["chan"] ) )
                        self.state["inchan"] = True

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

    def scanner( self ):
        while True:
            self.dorker.getlinks()
            sleep( 5 )


if __name__ == "__main__":

    server = None
    port = None
    enable_ssl = None
    nick = None
    chan = None

    def signal_handler( signal, frame ):
        print "[!] Shutting down"
        sys.exit( 0 )

    parser = argparse.ArgumentParser( "dork for vulnerabilities" )
    parser.add_argument( "-s", "--server", required=True, help="server to connect to" )
    parser.add_argument( "-p", "--port", required=True, help="port to connect to" )
    parser.add_argument( "-e", "--ssl", required=False, help="enable SSL", action="store_true" )
    parser.add_argument( "-n", "--nick", required=True, help="nick to identify with" )
    parser.add_argument( "-c", "--chan", required=True, help="chan to spam" )

    args = vars( parser.parse_args() )
    
    server = args["server"] if args["server"] else None
    port   = args["port"] if args["port"] else None
    enable_ssl = args["ssl"] if args["ssl"] else False
    nick = args["nick"] if args["nick"] else None
    chan = args["chan"] if args["chan"] else None

    signal.signal( signal.SIGINT, signal_handler )
    print "[+] Press Ctrl+C to quit"

    core = Core( server, port, enable_ssl, nick, chan )
