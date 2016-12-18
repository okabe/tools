#!/bin/bash

stub=$1
host=$( echo $stub | cut -f1 -d: )
port=$( echo $stub | cut -f2 -d: )

echo "[+] The following weak cipher algorithms are supported:"
ssh -p $port -o BatchMode=yes -vv test@$host 2>&1 \
    | grep "kex_parse_kexinit" \
    | cut -f3 -d: \
    | tr ',' '\n' \
    | grep arcfour \
    | sort -u \
    | while read line ; do
        echo " $line"
    done
