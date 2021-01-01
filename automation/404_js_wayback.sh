#!/bin/bash

url=$1

status_code=$(echo $url | httpx -x HEAD -status-code -silent -no-color | grep -oP '(?<=\[).*(?=\])')

if [[ $status_code != 200 ]]
then
printf "https://web.archive.org/web/20060102150405if_/$url\n"
fi
