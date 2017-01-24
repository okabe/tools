#!/bin/bash

host=$( echo $1 | cut -f1 -d: )
port=$( echo $1 | cut -f2 -d: )

for proto in ssl2 ssl3 ; do
    req="GET / HTTP/1.0\r\n\r\n"
    ( echo -en $req ; sleep 1 ) | ./openssl s_client \
        -$proto \
        -connect $host:$port 2>/dev/null >/dev/null \
        && echo "[+] $host supports $proto" \
        || echo "[!] $host does not support $proto" ;
done
