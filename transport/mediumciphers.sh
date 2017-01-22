#!/bin/bash

./openssl ciphers -v 'ALL' \
    | grep 168 \
    | while read line ; do
        c=$( echo $line | awk '{print $1}' )
        (echo -en "GET / HTTP/1.0\r\n\r\n" ; sleep 1) | ./openssl s_client \
            -connect $1 \
            -cipher $c 2>/dev/null >/dev/null \
            && echo "[+] Supports: $line" \
            || "[!] Unsupported: $line"
    done
