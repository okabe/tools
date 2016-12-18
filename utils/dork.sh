#!/bin/bash
#could almost just be an alias, just a quick and dirty for dorking things
#also note this should be improved to just use regex

lynx -dump "$1" | grep -E "Similar|Cached" | cut -f1 -d- | grep -vE "Similar|Cached" | cut -c4- | sort -u
