#!/bin/bash

stdin=$(</dev/stdin)

array=()
for i in {a..z} {A..Z} {0..9}; do
    array[$RANDOM]=$i
done
random_str=$(printf %s ${array[@]::23})

printf 'Fetching js files with subjs tool..\n'
printf ${stdin} | subjs | tee tmp/subjs${random_str}.txt >/dev/null    ## fetching js files with subjs tool

printf 'Launching Gau..\n'
printf ${stdin} | gau -random-agent | tee tmp/gau${random_str}.txt >/dev/null   ##gau

printf 'Now crawling web pages..\n'
printf ${stdin} | hakrawler -js -plain -subs -insecure | tee tmp/spider${random_str}.txt >/dev/null   ##just crawling web pages
## maybe it'll give different results than subjs

## searching for URLs in github
printf 'Searching for URLs in GH..\n'
printf ${stdin} | python3 -c "import re,sys; str0=str(sys.stdin.readlines()); str1=re.search('(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]', str0);  print(str1.group(0)) if str1 is not None else exit()" | xargs -I{} python3 ~/scripts/github-search/github-endpoints.py -d {} | tee tmp/gh${random_str}.txt >/dev.null
    
## sorting out all the results
cat tmp/subjs${random_str}.txt tmp/gau${random_str}.txt tmp/gh${random_str}.txt | cut -d '?' -f1 | grep -E '\.js(?:onp?)?$' | sort -u | tee tmp/all_js_files${random_str}.txt >/dev/null 

## save all endpoints to the file for future processing
cat tmp/all_js_files${random_str}.txt | parallel -j 20 "python3 js_extract.py -f {} | tee -a tmp/all_endpoints${random_str}.txt"
cat tmp/all_endpoints${random_str}.txt | sort -u  | tee tmp/all_endpoints_unique${random_str}.txt >/dev/null

## credentials checking
cat tmp/all_js_files${random_str}.txt | parallel -j 20 "python3 /root/scripts/SecretFinder/SecretFinder.py -o cli -i {}"

## parameters bruteforcing with modified Arjun
cat tmp/all_endpoints_unique${random_str}.txt | parallel -j 20 'python3 /root/scripts/Arjun/arjun.py -f /root/scripts/Arjun/db/big.txt -t 12 --get -u {}'


rm tmp/subjs${random_str}.txt tmp/gau${random_str}.txt tmp/spider${random_str}.txt tmp/gh${random_str}.txt tmp/all_js_files${random_str}.txt tmp/all_endpoints${random_str}.txt tmp/all_endpoints_unique${random_str}.txt
