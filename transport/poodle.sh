#!/bin/bash
./openssl ciphers | tr ':' '\n' | grep -i cbc | while read c ; do
    ./openssl s_client -ssl3 -connect $1 \
        -cipher $c < /dev/null 2>/dev/null >/dev/null && echo "[+] $c is enabled" ;
done
