#!/bin/bash
./openssl ciphers | tr ':' '\n' | while read c ; do
    ./openssl s_client -ssl2 -connect $1 \
        -cipher $c < /dev/null 2>/dev/null >/dev/null && echo "[+] $c is enabled" ;
done
