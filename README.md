<img width="599" alt="Screenshot 2020-12-30 at 13 09 55" src="https://user-images.githubusercontent.com/38838852/103442471-1dc53680-4c5f-11eb-9fac-5e0a07e87125.png">

Javascript security analysis (JSA) is a program for javascript analysis during web application security assessment.

# Capabilities of jsa.py:

- Looking for js files inside the first, second, and third-level js files. For example, http(s)://host.com/file.js contains a string "https://host.com/file.js" which could be different from already known 1st level js files and have additional endpoints or secrets.
- Displaying endpoints for the first, second, and third-level js files.
- Modifying found endpoints in the javascript file from /endpoint to http(s)://host_from_js_file.com/endpoint. This approach is handy when you have a massive list of javascript files and want to collect a list of all URLs.
- Excluding and printing 3rd party js files like https://googleapis.com or //facebook.net (most likely 2nd level js file) to reduce script runtime and remove unnecessary endpoints. It is useful to identify 3rd party js files since we can expand our attack surface and exploit vulnerabilities on a 3rd party website to change the javascript file.
- Checking the http code of the second and third level js files using the HEAD method. If 200 - it goes for further processing (because all js files should have a 200 code; otherwise, there will be no loading on the page). If 404 - then such a code indicates a non-existing file that can be uploaded by an attacker for insertion on the target page.
- Removing duplicates - js files and endpoints. By default, most of the js grabbing tools (like subjs, gau, etc) can provide a list of js files containing duplicates. Even if they performed a deduplication procedure, a list could still have duplicates since, for example, http(s)://host.com/file.js and http(s)://host.com/file.js?identifier=random_str are the same js files. Deleting duplicates can significantly boost the program's performance.
- Removing unnecessary lines with non-word characters (not a-z0-9 - http(s)://domain.com/().|[]{},), 1 word character (like http(s)://domain.com/1|a|1a - most likely to be js variable and not useful endpoint) and such extensions .css|.png|.jpg|.svg|.jpeg|.ico|.gif|.woff|.woff2|.swf.

[![asciicast](https://asciinema.org/a/0QzWKOxR18fStv7rxIkgrzt2I.svg)](https://asciinema.org/a/0QzWKOxR18fStv7rxIkgrzt2I)

# Capabilities of automation.sh:

- Searching for js files for provided host (http(s)://host.tld) in stdin using:
  - Wayback Machine (GAU), - launching wayback with `mimetype:(application|text)/javascript` to reduce execution time;
  - subjs tool;
  - Crawling (hakrawler) (classic crawling for js files only with `depth 1`; it could give different results than subjs tool)
  - GitHub search (github.py; it could give some unique results, too but it's time-consuming considering GH api rate-limit)
- Extraction of js files from js files.
- Printing endpoints.
-  Separating 200 OK js files from non-existent and processing Wayback Machine output. If js file parsed from wayback didn't return 200 OK, we are generating a URL (https://web.archive.org/web/20060102150405if_/$url) to see a file's content on wayback's server; it's ~useless for endpoints discovery but there is a point to search for credentials in the old content - that's what we'll do.
- Checking for credentials leakage using nuclei and a custom template containing 957 regexes on:
  - Alive js files (200 OK on the target host);
  - A copy of deleted js files from Wayback Machine.
- Parameters discovery on found endpoints using modified Arjun (it still needs some improvements).

<img width="966" alt="Screenshot 2021-01-02 at 17 27 21" src="https://user-images.githubusercontent.com/38838852/103461010-ad341d80-4d23-11eb-82ca-398f0bd1c573.png">

# Usage & installation for jsa.py:
git clone https://github.com/w9w/JSA.git && cd JSA && pip3 install -r requirements.txt

echo "https://host.com/file.js" | python3 jsa.py

Example for pulling out js files and processing:

echo "https://subdomain.host.com" | subjs | python3 jsa.py

# Usage & installation for automation.sh:

chmod +x automation.sh

paste your github API key into the `.tokens` file

echo "http(s)://host.com" | ./automation.sh

# Usage for massive and parallel scanning (~lightning-fast execution):

cat ~/lists/domains/host.com/http_s_hosts.txt | subjs | parallel -j 20 'echo "{}" | python3 jsa.py'.

You can get parallel GNU here https://www.gnu.org/software/parallel/. Don't forget to delete that annoying message.
  
### Roadmap:

- ✅ replace \[]// with http(s) host.tld /, if it exists;
- ✅ deletion of duplicate files of the second level about the files of the first level;
- ✅ setting the js file in the parameter when calling the program, still saving stdin;
- ✅ output the second level js files **optionally**, by parameter;
- ✅ improve the exclusion of 3rd party scripts by domain for multiple domains during bulk scanning, if possible;
- ✅ define domain and tld using re depending on line, if it's possible (yes but I need to update tlds constantly);
- ✅ credentials leak check using  ̶s̶e̶c̶r̶e̶t̶f̶i̶n̶d̶e̶r̶.̶p̶y̶ nuclei with extended regular expressions;
- ✅ brute-forcing parameters for endpoints using arjun.py;
- ⬜️ pull out every <script> part in the html page, analyzing it as a usual js file (saving and adding to the tool as file://);
- ⬜️ js files discovery via brute-force method (javascript content-type recognition) using enhanced version of https://s3.amazonaws.com/assetnote-wordlists/data/automated/httparchive_js_2020_11_18.txt;
- ⬜️ check available HTTP methods for endpoints (OPTIONS check);
- ⬜️ check whether endpoints should be applied to the host from the page itself or js file (CDNs, etc);
- ⬜️ retire js check via downloading js files to the temporary directory using wget (python module);
- ⬜️ recognition of dynamic js;
- ⬜️ save all found endpoints to a file **optionally**, by a parameter (maybe);
- ⬜️ save all found deep-level js files to a file **optionally**, by a parameter (maybe);
- ⬜️ rewrite a tool in Golang (I need to learn Golang first);
- ⬜️ multithreading, - only in Golang (multithreading in Python is terrible from my experience).

Special thanks to these beautiful people from who I s̶t̶e̶a̶l̶e̶d̶ borrowed some tools for automation.sh :D :

Corben Leo @lc for github.com/lc/subjs and github.com/lc/gau;

Luke Stephens @hakluke for github.com/hakluke/hakrawler;

Gwendal Le Coguic @gwen001 for https://github.com/gwen001/github-search/raw/master/github-endpoints.py;

Project discovery @projectdiscovery for github.com/projectdiscovery/nuclei and github.com/projectdiscovery/httpx;

Somdev Sangwan @s0md3v for https://github.com/s0md3v/Arjun (I needed to fork it for automation ease).

 ̶I̶n̶t̶e̶n̶d̶e̶d̶ ̶f̶e̶a̶t̶u̶r̶e̶s̶ known bugs:
 - Absolute paths could be incorrect in some cases;
 - Arjun doesn't have good calibration and can return as many parameters as you have in the wordlist;
 - Sometimes, the tool thinks that the 2nd/3rd js file is an endpoint and vise versa - I'll try to improve the detection;
 - If a host responds for too long, there could be an error - I'll try to suppress this exception in the script;
 - 3rd party js files identify regarding js file's URL, not the parent host.

# Ways to contribute

- Suggest a useful feature
- Report a bug
- Fix something and open a pull request
- Create a burp suite plugin
- Spread the word
