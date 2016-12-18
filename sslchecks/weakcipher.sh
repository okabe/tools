#!/bin/bash

null="/dev/null"
./openssl ciphers -v 'ALL:eNULL' \
    | grep -Ev '128|168|256' \
    | sort -u \
    | while read line ; do
        c=$( echo $line | awk '{print $1}' ) ;
        ./openssl s_client -cipher $c \
            -connect $1 \
            -starttls pop3 < $null 2> $null > $null \
                && echo "$line" ;
      done
