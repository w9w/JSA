printf "Subjs installation.. (Thanks to Corben Leo :) )\n\n"
GO111MODULE=on go get -u -v github.com/lc/subjs

printf "Gau installation.. (Thanks to Corben Leo :) )\n\n"
GO111MODULE=on go get -u -v github.com/lc/gau

printf "Hackrawler installation.. (Thanks to Luke Stephens :) )\n\n"
GO111MODULE=on go get -u -v github.com/hakluke/hakrawler

printf "github-endpoints.py wgetting.. (Thanks to Gwendal Le Coguic :) )\n\n"
wget https://github.com/gwen001/github-search/raw/master/github-endpoints.py

printf "Nuclei & httpx installation.. (Thanks to @m4ll0k :) )\n\n"
GO111MODULE=on go get -u -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei

GO111MODULE=on go get -u -v github.com/projectdiscovery/httpx/cmd/httpx

printf "Arjun installation.. (Thanks to Somdev Sangwan :) )\n\n"
git clone https://github.com/w9w/Arjun.git

chmod +x automation.sh
chmod +x automation/404_js_wayback.sh
