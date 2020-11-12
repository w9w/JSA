#/bin/bash

url=$1

status_code=$(echo $url | httpx -status-code -silent -no-color | grep -oP '(?<=\[).*(?=\])')

if [[ $status_code != 200 ]]
then
printf "https://web.archive.org/web/20060102150405/$url"
fi
