#!/bin/bash

GET="GET / HTTP/1.0\r\n\r\n"
host="-connect $1"
cipher="-cipher EDH"
STK="Server Temp Key"
(echo -en $GET ; sleep 1) \
    | openssl s_client $host $cipher 2>&1 \
    | grep $STK \
    | cut -f2 -d: \
    | awk '{print $2}' \
    | while read key ; do
        if [ $key -lt 2048 ] ; then
            echo "[+] Host is vulnerable to logjam"
        else
            echo "[!] Host is not vulnerable"
        fi
      done
