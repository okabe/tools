#!/bin/bash
#just cause im lazy and its nicer to avoid having to bang out 1 liners that are destined to be used again
#look for intersting keywords in pdf documents, run this script in whatever dir you have saved a bunch of pdf's in
#this depends on my other script called catpdf.py which I currently have saved as catpdf

ls | while read file ; do
    echo "[+] Checking $file"
    catpdf "$file" | grep -noiE "login|password|remote access|information asset|information|web access|webaccess|private|trade secret|technical|confidential|proprietary|secret|intellectual property|process|protected|technology" | while read result ; do
        ln=$( echo $result | cut -f1 -d: ) 
        string=$( echo $result | cut -f2 -d: ) ;
        echo " |- Found \"$string\" in $file on line $ln"
    done | sort -u
done
