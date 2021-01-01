#!/bin/bash

stdin=$(</dev/stdin)

array=()
for i in {a..z} {A..Z} {0..9}; do
    array[$RANDOM]=$i
done
random_str=$(printf %s ${array[@]::23})

## fetching js files with subjs tool


printf 'Fetching js files with subjs tool..\n'
printf $stdin | subjs | tee tmp/subjs${random_str}.txt >/dev/null


## lauching wayback with a "js only" mode to reduce execution time
printf 'Launching Gau with wayback..\n'
printf $stdin | xargs -I{} echo "{}/*&filter=mimetype:application/javascript&somevar=" | gau -providers wayback -random-agent | tee tmp/gau${random_str}.txt >/dev/null   ##gau
printf $stdin | xargs -I{} echo "{}/*&filter=mimetype:text/javascript&somevar=" | gau -providers wayback -random-agent | tee -a tmp/gau${random_str}.txt >/dev/null   ##gau


## if js file parsed from wayback didn't returne 200 live, we are generating a URL to see a file's content on wayback's server;
## it's useless for endpoints discovery but there exists a point to search for credentials in the old conteent; that's what we'll do
## only wayback as of now

printf "Fetching a content of 404 js files from wayback.."
cat tmp/gau${random_str}.txt | cut -d '?' -f1 | cut -d '#' -f1 | sort -u | parallel "printf '{}' | tee tmp/gau200ok${random_str}.txt >/dev/null && automation/./404_js_wayback.sh '{}' | tee -a tmp/creds_search${random_str}.txt >/dev/null"


## Classic crawling. It could give different results than subjs tool
printf 'Now crawling web pages..\n'
printf $stdin | hakrawler -js -plain -subs -insecure -depth 3 | tee tmp/spider${random_str}.txt >/dev/null   ##just crawling web pages


## Searching for URLs in github, - that could give some unique results, too
## python one-liner - for clear domain matching

printf 'Searching for URLs in GH..\n'
printf ${stdin} | python3 -c "import re,sys; str0=str(sys.stdin.readlines()); str1=re.search('(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]', str0);  print(str1.group(0)) if str1 is not None else exit()" | xargs -I{} python3 github-endpoints.py -d {} | grep '\.js' | tee tmp/gh${random_str}.txt >/dev.null
    
    
## sorting out all the results

##that's for creds_check

cat tmp/subjs${random_str}.txt tmp/gau200ok${random_str}.txt tmp/gh${random_str}.txt tmp/spider${random_str}.txt | cut -d '?' -f1 | cut -d '#' -f1 | grep -E '\.js(?:onp?)?$' | sort -u | tee tmp/all_js_files${random_str}.txt >/dev/null 

## save all endpoints to the file for future processing

## extracting js files from js files
printf "Printing deep-level js files..\n"
cat tmp/all_js_files${random_str}.txt | parallel "printf '{}' | python3 automation/js_files_extraction.py | tee -a tmp/all_js_files${random_str}.txt"

printf "Searching for endpoints..\n"
cat tmp/all_js_files${random_str}.txt | parallel "python3 automation/endpoints_extraction.py -f {} | tee -a tmp/all_endpoints${random_str}.txt"
cat tmp/all_endpoints${random_str}.txt | sort -u  | tee tmp/all_endpoints_unique${random_str}.txt >/dev/null

## credentials checking

printf "Checking our sweet js files for credentials.."
cat tmp/all_js_files${random_str}.txt tmp/creds_search${random_str}.txt | parallel "nuclei -t templates/credentials-disclosure-all.yaml -nC -silent -target {}"


## parameters bruteforcing with modified Arjun

printf "Arjun parameters discovery.."
cat tmp/all_endpoints_unique${random_str}.txt | parallel "python3 Arjun/arjun.py -f Arjun/db/params.txt -t 12 --get -u {}"


rm tmp/subjs${random_str}.txt tmp/gau${random_str}.txt tmp/gau200ok${random_str}.txt tmp/spider${random_str}.txt tmp/gh${random_str}.txt tmp/all_js_files${random_str}.txt tmp/all_endpoints${random_str}.txt tmp/all_endpoints_unique${random_str}.txt
