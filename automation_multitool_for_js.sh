#!/bin/bash

stdin=$(</dev/stdin)

cat $(stdin) | parallel -j 30 ' echo "{}" | subjs | tee -a subjs.txt >/dev/null'    ## fetching js files with subjs tool

cat $(stdin) | parallel -j 30 'echo {} | gau -random-agent | tee -a gau.txt >/dev/null'   ##gau

cat $(stdin) | parallel -j 15 'echo {} | hakrawler -js -plain -subs -insecure | tee -a spider.txt >/dev/null'   ##just crawling web pages
## maybe it'll give different results than subjs

## searching for URLs in github
cat $(stdin) | parallel -j 15 "echo {} | python3 -c \"import re,sys; str0=str(sys.stdin.readlines()); str1=re.search('(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]', str0);  print(str1.group(0)) if str1 is not None else exit()\" | xargs -I{} python3 ~/scripts/github-search/github-endpoints.py -d {} | tee -a gh.txt >/dev.null"
    
## sorting out all the results
cat subjs.txt gau.txt gh.txt | cut -d '?' -f1 | grep -E '\.js(?:onp?)?$' | sort -u | tee all_js_files.txt >/dev/null 

## save all endpoints to the file for future processing
cat all_js_files.txt | parallel "js_extract.py | tee -a all_endpoints.txt"

## credentials checking
cat all_endpoints.txt | parallel -j 15 "python3 /root/scripts/SecretFinder/SecretFinder.py -o cli -i {}"

## parameters bruteforcing with modified Arjun
cat all_endpoints.txt | parallel -j 20 'python3 /root/scripts/Arjun/arjun.py -f /root/scripts/Arjun/db/big.txt -t 12 --get -u {}'
