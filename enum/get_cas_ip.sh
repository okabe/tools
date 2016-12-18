#!/bin/bash

#http://foofus.net/?p=758

request="GET /autodiscover/autodiscover.xnl HTTP/1.0\r\n\r\n"
(echo -en $request ; sleep 1 ) | openssl s_client -connect $1 2>&1 \
    | awk '/Extended master secret/{y=1;next}y' 2>/dev/null
