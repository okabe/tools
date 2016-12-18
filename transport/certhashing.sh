#!/bin/bash

./openssl s_client -connect $1 < /dev/null 2>/dev/null \
    | ./openssl x509 -noout -text \
    | grep "Signature Algorithm" \
    | cut -f2 -d: \
    | sort -u \
    | while read sig ; do
        echo "[+] Certificate Hashing Algorithm: $sig"
    done
