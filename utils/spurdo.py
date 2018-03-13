#!/usr/bin/env python2

from random import choice
import sys

def spurdo( phrase, threshold=5 ):
    replacements = {
        "america"    : "clapistan",
        "capitalism" : "clapistan",
        "communism"  : "gomunesm",
        "meme"       : "maymay",
        "some"       : "some",
        "epic"       : "ebin",
        "kek"        : "geg",
        "right"      : "rite",
        "love"       : "loab",
        "money"      : "dolar",
        "ing"        : "ign",
        "alk"        : "olk",
        "og"         : "awg",
        "ie"         : "ei",
        "ex"         : "egz",
        "my"         : "muh",
        "ng"         : "nk",
        "ic"         : "ig",
        "ys"         : "yz",
        "ws"         : "wz",
        "us"         : "uz",
        "ts"         : "tz",
        "ss"         : "sz",
        "rs"         : "rz",
        "ns"         : "nz",
        "ms"         : "mz",
        "ls"         : "lz",
        "is"         : "iz",
        "gs"         : "gz",
        "fs"         : "fz",
        "es"         : "ez",
        "ds"         : "dz",
        "bs"         : "bz",
        "tr"         : "dr",
        "ts"         : "dz",
        "pr"         : "br",
        "nt"         : "dn",
        "lt"         : "ld",
        "kn"         : "gn",
        "cr"         : "gr",
        "ck"         : "gg",
        "va"         : "ba",
        "up"         : "ub",
        "pi"         : "bi",
        "pe"         : "be",
        "po"         : "bo",
        "ot"         : "od",
        "op"         : "ob",
        "nt"         : "nd",
        "ke"         : "ge",
        "iv"         : "ib",
        "et"         : "ed",
        "ev"         : "eb",
        "co"         : "go",
        "ck"         : "gg",
        "ca"         : "ga",
        "ap"         : "ab",
        "af"         : "ab",
        "az"         : "ez",
        "ov"         : "ob",
        "av"         : "eb",
        "th"         : "d",
        "mm"         : "m",
        "wh"         : "w",
        "ll"         : "l",
        "t"          : "d",
        "k"          : "g"
    }
    
    count = 0
    new_phrase = []
    for word in phrase.split():
        orig_word = word
        while ( count != threshold ):
            elem = choice( [ x for x in range( len( replacements ) ) ] )
            key = replacements.keys()[elem]
            word = word.replace( key, replacements[key] )
            count += 1
        if orig_word == word:
            for key in replacements:
                word = word.replace( key, replacements[key] )
        new_phrase.append( word )
    return " ".join( new_phrase )

if __name__ == "__main__":
    print spurdo( " ".join( sys.argv[1:] ) )
