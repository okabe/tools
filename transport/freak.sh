#!/bin/bash

null="/dev/null"
./openssl ciphers EXPORT -v \
    | tr ':' '\n' \
    | sort -u \
    | while read line ; do
        c=$( echo $line | awk '{print $1}' ) ;
        ( echo -en "QUIT" ; sleep 1 ) \
            | ./openssl s_client -cipher $c \
            -connect $1 \
            -starttls pop3 2>$null >$null \
            && echo "$line" ;
      done
