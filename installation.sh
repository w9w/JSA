#bin/bash

printf "Subjs installation.. (Thanks to Corben Leo :) )\n\n"
go install github.com/lc/subjs@latest

printf "Gau installation.. (Thanks to Corben Leo :) )\n\n"
go install github.com/lc/gau@latest

printf "Hackrawler installation.. (Thanks to Luke Stephens :) )\n\n"
go install github.com/hakluke/hakrawler@latest

printf "github-endpoints.py wgetting.. (Thanks to Gwendal Le Coguic :) )\n\n"
wget https://github.com/gwen001/github-search/raw/master/github-endpoints.py

printf "Nuclei & httpx installation.. (Thanks to @projectdiscovery :) )\n\n"
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

printf "Arjun installation.. (Thanks to Somdev Sangwan :) )\n\n"
git clone https://github.com/w9w/Arjun.git

printf "tldextract python module installation ..."
pip3 install tldextract

mkdir tmp
chmod +x automation.sh
chmod +x automation/404_js_wayback.sh
