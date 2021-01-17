#!/usr/bin/env python3
import re
import requests
import io
import os
import argparse
import sys
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tld_detection import tld_detection

## Implement reading from specified file

parser = argparse.ArgumentParser()
parser.add_argument('-v', "--verbose", help='verbose', action='store_true')
parser.add_argument('-e', "--exclude", help='exclude & print 3rd party js files', action='store_true')
parser.add_argument('-f', "--file", help='js file URL in format htt(p|ps)://(.*)/name.js', action='append')

verbose = parser.parse_args().verbose
exclude = parser.parse_args().exclude
if not sys.stdin.isatty():
    global js_file
    js_file = sys.stdin.readlines()
elif parser.parse_args().file:
    js_file = parser.parse_args().file
else:
    print("Please specify js file in STDIN or in argument -f!")
    exit()

# js_file = open("/Users/max/test13.txt", "r").readlines()


## just some containers for future values

original_lines = []

all_endpoints_1st_lvl = []
all_endpoints_original = []
js_files_2nd_lvl = []

all_endpoints_2nd_lvl = []
all_endpoints_2nd_lvl_original = []
js_files_3rd_lvl = []

all_endpoints_3rd_lvl = []
all_endpoints_3rd_lvl_original = []
tmp_list = []
js_files_4th_lvl = []  ## just for passing it to the main func, it won't be processed actually


####
# now = datetime.now()
# now = str(now).replace(" ", "_").replace(":", "-")
# now = re.sub("\..*?$", "", now)

# curpath = os.path.abspath(os.curdir)

# directory_with_js_files = "%s/js_files/%s/" % (curpath, now)  ## directory of downloaded js files for other tools


###

def deduplication(input, original_lines):  ## filtering + deduplication
    existing_lines = []
    for line in input:  ## Filtering the output of subjs (#$ and ?v=$)
        line = re.sub("\\?v=.*?$", "", line)
        line = re.sub("#.*?$", "", line)
        existing_lines.append(line)
    for line in existing_lines:  ## Deleting duplicates
        line = line.strip()
        if line not in original_lines:
            original_lines.append(line)


def main_func(original_lines, js_files, all_endpoints):
    for line in original_lines:  ## main loop

        clear_url0 = re.findall("^(.*?)\\b/", line)
        global clear_url
        clear_url = re.sub("\['|'\]", "", str(clear_url0))  ## matching URL without js part
        domain_name = tld_detection(clear_url)
        if "[]" in clear_url:
            continue
        if str(domain_name) not in str(line) and exclude is True:
            ## excluding 3rd party js files & print 'em

            print("Possible (if not CDN) 3rd party JS file has been found: " + line)
        warnings.simplefilter('ignore', InsecureRequestWarning)
        try:
            js_file_status = requests.get(line, verify=False).status_code  ## finding out a status code of js file url
        except Exception:
             pass
        if js_file_status == 200:  ## if js file exists (to reduce time)
            warnings.simplefilter('ignore', InsecureRequestWarning)
            js_file_content = requests.get(line, verify=False)  ## fetching js file's content

            # filename = "%s/%s" % (directory_with_js_files, name_for_wget)
            # os.makedirs(os.path.dirname(filename))  ##creating dir with a js file
            # js_file_write = open(filename, "w")  ## it's for js file downloading

            # js_file_write.write(js_file_content.text)  ## wget for js file into the directory

            u = re.findall("\"\/[a-zA-Z0-9_?&=/\-\#\.]*\"", js_file_content.text)  ## matching "string"
            u = str(u).replace("', '", "\n").replace("[]", "")
            u = re.sub("\['|'\]|\"", "", u)
            u = re.sub(
                ".css|.png|.jpg|.svg|.jpeg|.ico|.gif|.woff|.woff2|.swf", "", u,
                flags=re.M)  ## excluding not desirable file extensions
            u = re.sub(".*?\.(facebook|twitter).(net|com)(/)|(/|/\?|/#|#)$", "", u,
                       flags=re.M)  ##preparing for deduplication with / /? # deleting
            u = re.sub("(\n\n)", "\n", u, flags=re.M)

            if re.findall("^//", u):
                u = re.sub("^//(.*?)/", clear_url + "/", u, flags=re.M)  ## it's for js files
            else:
                u = re.sub("^", clear_url, u, flags=re.M)
            u_lines = io.StringIO(u).readlines()  ## endpoints

            for one in u_lines:
                if re.findall("\.js$", one):
                    if re.findall("^//", one) and verbose is True:  ## excluding 3rd party 2nd lvl js files & print 'em
                        if not re.findall("^//%s" % domain_name, one):
                            print("Possible (if not CDN) 3rd party JS file has been found: " + one)
                    if re.findall("^//", one):
                        one = re.sub("^//(.*?)/", clear_url + "/", one)  # one = re.sub("\n", "", one)
                        js_files.append(one)
                    if re.findall("^/", one):
                        one = re.sub("^/", clear_url + "/", one)
                    if re.findall("^\b", one):  ## if js file doesn't have / at ^, it'll be added
                        one = re.sub("^", clear_url + "/", one)  # one = re.sub("\n", "", one)
                        js_files.append(one)
                    if re.findall("^\[\]/", one):
                        one = re.sub("^\[\]", clear_url, one)
                        js_files.append(one)
                    else:  ## printing js files found on 2nd level
                        js_files.append(one)
                else:
                    all_endpoints.append(one)  ## printing 1st lvl endpoints
        elif js_file_status == 404 and verbose is True:  ## todo make it for subjs output only
            print(
                "JS file {} returned 404 code. Check the host and try to apply file upload with path traversal/PUT method file upload.".format(
                    line))


deduplication(js_file, original_lines)
main_func(original_lines, js_files_2nd_lvl, all_endpoints_1st_lvl)

if len(all_endpoints_1st_lvl) != 0:
    temp0 = []
    for l in all_endpoints_1st_lvl:

        clear_domain = re.findall("http(s)://(.*)(?=/)", l)
        clear_domain = re.findall(", '(.*?)'", str(clear_domain))
        clear_domain = ''.join(clear_domain)

        t = re.findall("^(.*?)(?<=com)", l)
        l = re.sub("(/|/\?|/#|#|/\.)$", "", l)  ## additionally deleting / /? /#

        if not re.findall("%s$" % clear_domain,
                          l):  ## removing clear urls without actual endpoints like http(s)://domain.com
            if "[]//" in l:
                l = l.replace("[]//", "//%s" % clear_domain)
                temp0.append(l)

            if not re.findall("%s/\W" % clear_domain, l):  ## deleting endpoints containing
                ## non-word character (not a-z0-9) http(s)://domain.com/(.|[]{},
                if not re.findall("%s/[a-z0-9]{1}$" % clear_domain,
                                  l):  ## deleting endpoints containing 1 word character like http(s)://domain.com/1|a|1a;
                    temp0.append(l)  ## most likely to be an endpoint and not a javascript variable

    all_endpoints_1st_lvl.clear()  ## deleting current list w/ endpoints
    all_endpoints_1st_lvl = temp0  ##substitution

    deduplication(all_endpoints_1st_lvl, all_endpoints_original)  ## deleting dupes
    for l in all_endpoints_original:  ## printing a list
        if "[]" in l:
            continue
        else:
            print(l)

if len(js_files_2nd_lvl) != 0:  ## processing 2nd level js files
    printed = False
    js_files_2nd_lvl_original = []
    deduplication(js_files_2nd_lvl, js_files_2nd_lvl_original)  ## removing dupes
    for l in js_files_2nd_lvl_original:  ## printing a list

        j2 = re.findall("\.js$", l)  ## sometimes (I don't know why though), non-js files leak to the list
        if len(j2) == 0:
            continue
        if l not in original_lines:
            if printed is False and verbose is True:                ## printing a text only one time if verbose mode
                print("\nJS files 2nd level:\n")
                printed = True
            if verbose is True:
                print(l)

    main_func(js_files_2nd_lvl_original, js_files_3rd_lvl, all_endpoints_2nd_lvl)

if len(js_files_3rd_lvl) != 0:
    printed = False
    js_files_3rd_lvl_original = []
    deduplication(js_files_3rd_lvl, js_files_3rd_lvl_original)  ## removing dupes
    for l in js_files_3rd_lvl_original:  ## printing a list

        j3 = re.findall("\.js$", l)  ## sometimes (I don't know why though), non-js files leak to the list
        if len(j3) == 0:
            continue
        if l not in js_files_2nd_lvl_original and original_lines:
            if printed is False and verbose is True:                ## printing a text only one time if verbose mode
                print("\nJS files 3rd level:\n")
                printed = True
            if verbose is True:
                if re.findall("^htt(p|s)(.*?)\w//(.*?)/", l):
                    l = re.sub("^htt(p|s)(.*?)\w//(.*?)/", clear_url + "/", l, flags=re.M)
                print(l)

    main_func(js_files_3rd_lvl, js_files_4th_lvl, all_endpoints_3rd_lvl)



if all_endpoints_2nd_lvl:  ## printing 2nd level endpoints
    temp1 = []
    for l in all_endpoints_2nd_lvl:

        clear_domain = re.findall("http(s)://(.*)(?=/)", l)
        clear_domain = re.findall(", '(.*?)'", str(clear_domain))
        clear_domain = ''.join(clear_domain)

        t = re.findall("^(.*?)(?<=com)", l)
        l = re.sub("(/|/\?|/#|#|/\.)$", "", l)  ## additionally deleting / /? /#

        if not re.findall("%s$" % clear_domain,
                          l):  ## removing clear urls without actual endpoints like http(s)://domain.com
            if "[]//" in l:
                l = l.replace("[]//", "//%s" % clear_domain)
                temp1.append(l)

            if not re.findall("%s/\W" % clear_domain, l):  ## deleting endpoints containing
                ## non-word character (not a-z0-9) http(s)://domain.com/(.|[]{},
                if not re.findall("%s/[a-z0-9]{1}$" % clear_domain,
                                  l):  ## deleting endpoints containing 1 word character like http(s)://domain.com/1|a|1a;
                    temp1.append(l)  ## most likely to be an endpoint and not a javascript variable

    all_endpoints_2nd_lvl.clear()  ## deleting current list w/ endpoints
    all_endpoints_2nd_lvl = temp1  ##substitution
    printed = False
    deduplication(all_endpoints_2nd_lvl, all_endpoints_2nd_lvl_original)    ## deleting dupes
    for l in all_endpoints_2nd_lvl_original:  ## printing a lists
        if "[]" in l:
            continue
        elif l not in all_endpoints_original:
            if printed is False and verbose is True:            ## printing a text only one time if verbose mode
                print("\nEndpoints 2nd level:\n")
                printed = True
            print(l)  ##printing URL with endpoint if it's original

if all_endpoints_3rd_lvl:
    all_endpoints_3rd_lvl_original = []
    temp2 = []
    for l in all_endpoints_3rd_lvl:

        clear_domain = re.findall("http(s)://(.*)(?=/)", l)
        clear_domain = re.findall(", '(.*?)'", str(clear_domain))
        clear_domain = ''.join(clear_domain)

        t = re.findall("^(.*?)(?<=com)", l)
        l = re.sub("(/|/\?|/#|#|/\.)$", "", l)  ## additionally deleting / /? /#

        if not re.findall("%s$" % clear_domain,
                          l):  ## removing clear urls without actual endpoints like http(s)://domain.com
            if "[]//" in l:
                l = l.replace("[]//", "//%s" % clear_domain)
                temp2.append(l)

            if not re.findall("%s/\W" % clear_domain, l):  ## deleting endpoints containing
                ## non-word character (not a-z0-9) http(s)://domain.com/(.|[]{},
                if not re.findall("%s/[a-z0-9]{1}$" % clear_domain,
                                  l):  ## deleting endpoints containing 1 word character like http(s)://domain.com/1|a|1a;
                    temp2.append(l)  ## most likely to be an endpoint and not a javascript variable

    all_endpoints_3rd_lvl.clear()  ## deleting current list w/ endpoints
    all_endpoints_3rd_lvl = temp2  ##substitution
    printed = False
    all_endpoints_2nd_lvl_original = []  ## deleting dupes
    deduplication(all_endpoints_3rd_lvl, all_endpoints_3rd_lvl_original)
    for l in all_endpoints_3rd_lvl_original:  ## printing a lists
        if "[]" in l:
            continue
        elif l not in all_endpoints_original and all_endpoints_2nd_lvl_original:
            if printed is False and verbose is True:
                print("Endpoints 3rd level:\n")
                printed = True
            print(l)

# if os.path.exists(directory_with_js_files) is True:
# os.system("retire %s" % directory_with_js_files)

## Deleting duplicates from the js files 2nd level

## Deleting duplicates from the endpoints 1st level

## Deleting duplicates from the js files 3rdnd level

## Deleting duplicates from the endpoints 2nd level
