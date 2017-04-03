[+] Setup:
 mkdir {wordlists,rules}
 cp /path/to/hashcat/install/rules/whatever_you_want.rule rules/
 cp /path/to/your/wordlists.txt wordlists/

[+] Run
 python2 hashcatirc.py -s irc.blackcatz.org -p 6697 -e -n "hashkiller" -c "#howtohack" -l wordlists -r rules -a cracked.log
