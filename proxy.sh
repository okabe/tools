#!/bin/bash                                                                                                            

proxy=$1
cmd=$2

if [[ $cmd == *"on"* ]]; then
    export http_proxy="$proxy"
    export https_proxy="$http_proxy"
    export ftp_proxy="$http_proxy"
    export rsync_proxy="$http_proxy"
    export no_proxy="localhost,127.0.0.1,localaddress,.localdomain.com"
    echo "Enabled proxy"
fi

if [[ $cmd == *"off"* ]]; then
    unset http_proxy
    unset HTTP_PROXY
    unset https_proxy
    unset HTTPS_PROXY
    unset ftp_proxy
    unset FTP_PROXY
    unset rsync_proxy
    unset RSYNC_PROXY
    echo "Disabled proxy"
fi
