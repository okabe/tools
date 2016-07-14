#!/usr/bin/env python2
# super simple but pretty useful for password analysis

import sys, re

lol = {}

for line in open( sys.argv[1], "r" ).readlines():
    
    line = line.rstrip( "\n" ).rstrip( ":::" )
    if "::" in line:
        line = line.replace( "::", ":WORKGROUP:" )

    stub = re.match( "^(.+):(.+):(.+):(.+)$", line )
    
    if stub:
        usr   = stub.group( 1 )
        dom   = stub.group( 2 )
        LM    = stub.group( 3 )
        NT    = stub.group( 4 ).rstrip( "\n" )
        
        if NT in lol:
            lol[NT].append( usr )
        else:
            lol[NT] = [usr]

for i in lol:
    print "{}:{}".format( i, lol[i] )
