#!/usr/bin/env python2

from BeautifulSoup import BeautifulSoup as Soup
import urllib2
import sys

def get_quote( ticker ):
    """ check last trade, todays change, todays open, todays range, 52w low/high, 
    volume, average volume, P/E, dividend yield, and market cap of ticker """

    days_last      = ""
    change         = ""
    change_percent = ""
    prev_close     = ""
    days_open      = ""
    bid            = ""
    ask            = ""
    low            = ""
    high           = ""
    f2wk_low       = ""
    f2wk_high      = ""
    volume         = ""
    avg_volume     = ""
    market_cap     = ""
    pe_ratio       = ""
    
    url = "https://ca.finance.yahoo.com/q?s={}".format( ticker )
    
    data = {
        "Accept"     : "text/html",
        "User-Agent" : "Mozilla/5.0"
    }
    
    request = urllib2.Request( url, headers=data )
    quote = Soup( urllib2.urlopen( request ).read() )

    for div in quote.findAll( "div", { "class" : "yfi_rt_quote_summary_rt_top sigfig_promo_0" } ):
        #days last
        for span in div.findAll( "span", { "class" : "time_rtq_ticker" } ):
            days_last = span.text
        #change
        for span in div.findAll( "span", { "class" : "up_g time_rtq_content" } ):
            status = ""
            for i in span.findAll( "span" ):
                for j in i.findAll( "img", { "class" : "pos_arrow" } ):
                    if "Up" or "Down" in str( j ):
                        if "Up" in str( j ):
                            status = "+"
                        else:
                            status = "-"
                        change = "{}{}".format( status, i.text )
                change_percent = "{}{}".format( status, i.text[1:-1] )

    for div in quote.findAll( "div", { "class" : "yui-u first yfi-start-content" } ):
        for tr in div.findAll( "tr" ):
            if "Prev Close" in tr.text:
                for td in tr.findAll( "td" ):
                    prev_close = td.text
            if "Open" in tr.text:
                for td in tr.findAll( "td" ):
                    days_open = td.text
            if "Bid" in tr.text:
                for td in tr.findAll( "td" ):
                    bid = td.text
            if "Ask" in tr.text:
                for td in tr.findAll( "td" ):
                    ask = td.text
            if "Day's Range" in tr.text:
                for td in tr.findAll( "td" ):
                    low  = td.text.split( "-" )[0]
                    high = td.text.split( "-" )[1]
            if "52wk Range" in tr.text:
                for td in tr.findAll( "td" ):
                    f2wk_low  = td.text.split( "-" )[0]
                    f2wk_high = td.text.split( "-" )[1]
            if "Volume" in tr.text:
                for td in tr.findAll( "td" ):
                    volume = td.text
            if "Avg Vol" in tr.text:
                for td in tr.findAll( "td" ):
                    avg_volume = td.text
            if "Market" in tr.text:
                for td in tr.findAll( "td" ):
                    market_cap = td.text
            if "P/E" in tr.text:
                for td in tr.findAll( "td" ):
                    pe_ratio = td.text

    print "Last:{} Change:{} ChangeRate:{} Close:{} Open:{} Bid:{} Ask:{} Low:{} High:{} 52wLow:{} 52wHigh:{} Volume:{} AvgVolume:{} MarketCap:{} P/E:{}".format( 
            days_last, 
            change, 
            change_percent,
            prev_close,
            days_open,
            bid,
            ask,
            low,
            high,
            f2wk_low,
            f2wk_high,
            volume,
            avg_volume,
            market_cap,
            pe_ratio
    )

get_quote( sys.argv[1] )
