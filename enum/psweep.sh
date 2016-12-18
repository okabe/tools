#!/bin/bash

cat $1 | while read ip ; do
  ping -c 1 -w 1 $ip > /dev/null \
      && echo "[+] Reply from $ip" \
      || echo "[!] Host $ip seems down"
done
