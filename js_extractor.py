import re
import requests
import io
import os
import argparse
import sys
import subprocess
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

js_file = sys.stdin.readlines()

parser = argparse.ArgumentParser()                  ## accepting domain name as a parameter name for 3rd party domains excluding
parser.add_argument("-d", "--domain", help="domain to test", action="append")
domain_name = str(parser.parse_args().domain).replace("['", "").replace("']", "")


## Implementing reading from a specific file

#js_file = open("/path/test12.txt", "r").readlines()


## multiple files as a tuple


#js_files = [']

original_lines = []

all_endpoints_1st_lvl = []
js_files_2nd_lvl = []

all_endpoints_2nd_lvl = []
js_files_3rd_lvl = []

####
now = datetime.now()
now = str(now).replace(" ", "_").replace(":", "-")
now = re.sub("\..*?$", "", now)

curpath = os.path.abspath(os.curdir)

directory_with_js_files = "%s/js_files/%s/" % (curpath, now)  ## directory of downloaded js files for other tools
###

def deduplication(input_file, original_lines):
    existing_lines = []
    for line in input_file:  ## Deleting duplicates from the output of subjs (#$ and ?v=$)
        line = re.sub("\\?v=.*?$", "", line)
        line = re.sub("#.*?$", "", line)
        existing_lines.append(line)
    for line in existing_lines:
        line = line.strip()
        if line not in original_lines:
            original_lines.append(line)


deduplication(js_file, original_lines)

def main_func(original_lines, js_files_2nd_lvl, all_endpoints_1st_lvl):
    for line in original_lines:  ## main loop

        tld = re.sub("^[a-z]+\.", "", domain_name)              ## matching TLD

        t = re.findall("^(.*?)(?<=%s)" %tld, line)
        clear_url = re.sub("\['|'\]", "", str(t))                   ## matching URL without js part

        if str(domain_name) not in str(line):  ## excluding 3rd party js files & print 'em
            print("3rd party JS file has been found: " + line)
            continue
        warnings.simplefilter('ignore', InsecureRequestWarning)

        js_file_status = requests.head(line, verify=False).status_code  ## fastly (HEAD) finding out a status code of js file url

        if js_file_status == 200:                                   ## if js file exists (to reduce time)
            warnings.simplefilter('ignore', InsecureRequestWarning)
            js_file_content = requests.get(line, verify=False)  ## fetching js file's content



            ##Preparations for retire js check
            ####
            #filename = "%s/%s" % (directory_with_js_files, name_for_wget)
            #os.makedirs(os.path.dirname(filename))  ##creating dir with a js file
            #js_file_write = open(filename, "w")  ## it's for js file downloading

            #js_file_write.write(js_file_content.text)  ## wget for js file into the directory

            ###

            u = re.findall("\"\/[a-zA-Z0-9_?&=/\-\#\.]*\"", js_file_content.text)  ## matching "string"
            u = str(u).replace("', '", "\n").replace("[]", "")
            u = re.sub("\['|'\]|\"", "", u)
            u = re.sub("^", clear_url, u, flags=re.M)
            u = re.sub(
                ".css|.png|.jpg|.svg|.jpeg|.ico|.gif|.woff|.woff2|.swf", "", u,
                flags=re.M)  ## excluding not desirable file extensions
            u = re.sub(".*?\.(facebook|twitter).(net|com)(/)|(/|/\?|/#|#)$", "", u,
                       flags=re.M)  ##preparing for deduplication with / /? # deleting
            u = re.sub("(\n\n)", "\n", u, flags=re.M)

            u_lines = io.StringIO(u).readlines()  ## endpoints

            for one in u_lines:
                if re.findall("\.js$", one):
                    if re.findall("^//", one):  ## excluding 3rd party 2nd lvl js files & print 'em
                        print("3rd party JS file has been found: " + one)
                    if re.findall("^\b", one):  ## if js file doesn't have / at ^, it'll be added
                        one = re.sub("^\b", clear_url + "/", one)  # one = re.sub("\n", "", one)
                        js_files_2nd_lvl.append(one)
                    else:  ## printing js files found on 2nd level
                        js_files_2nd_lvl.append(one)
                else:
                    all_endpoints_1st_lvl.append(one)  ## printing 1st lvl endpoints
        elif js_file_status == 404:
            print("JS file {} returned 404 code. Check the host and try to apply file upload with path traversal/PUT method file upload.".format(line))

main_func(original_lines, js_files_2nd_lvl, all_endpoints_1st_lvl)

temp = []
if len(all_endpoints_1st_lvl) != 0:

    for l in all_endpoints_1st_lvl:

        clear_domain = re.findall("http(s)://(.*)(?=/)", l)
        clear_domain = re.findall(", '(.*?)'", str(clear_domain))
        clear_domain = ''.join(clear_domain)

        t = re.findall("^(.*?)(?<=com)", l)
        l = re.sub("(/|/\?|/#|#|/\.)$", "", l)  ## additionally deleting / /? /#

        if not re.findall("%s$" % clear_domain, l):                         ## removing clear urls without actual endpoints like http(s)://domain.com
            if "[]//" in l:
                l = l.replace("[]//", "//%s" %clear_domain)
                temp.append(l)

            if not re.findall("%s/\W" %clear_domain, l):                ## deleting endpoints containing non-word character (not a-z0-9) http(s)://domain.com/(.|[]{},
                if not re.findall("%s/([a-z0-9]{1}/[a-z0-9]|[a-z0-9]{1}){1}$" % clear_domain, l):       ## deleting endpoints containing 1 word character like http(s)://domain.com/1|a
                    temp.append(l)                                          ## most likely to be an endpoint and not a javascript variable

    all_endpoints_1st_lvl.clear()  ## deleting current list w/ endpoints
    all_endpoints_1st_lvl = temp            ##substitution

    all_endpoints_original = []  ## deleting dupes
    deduplication(all_endpoints_1st_lvl, all_endpoints_original)
    for l in all_endpoints_original:  ## printing a list
        if "[]" in l:
            continue
        else:
            print(l)


js_files_2nd_lvl_original = []

if len(js_files_2nd_lvl) != 0:
    print("\nJS files 2nd level:\n")
    deduplication(js_files_2nd_lvl, js_files_2nd_lvl_original)  ## removing dupes
    for l in js_files_2nd_lvl_original:  ## printing a list

        j2 = re.findall("\.js$", l)
        if len(j2) == 0:
            continue
        else:
            print(l)

    main_func(js_files_2nd_lvl_original, js_files_3rd_lvl, all_endpoints_2nd_lvl)

if js_files_3rd_lvl:
    print("JS files 3rd level:\n")
    js_files_3rd_lvl_original = []
    deduplication(js_files_3rd_lvl, js_files_3rd_lvl_original)  ## removing dupes
    for l in js_files_3rd_lvl_original:  ## printing a list

        j3 = re.findall("\.js$", l)
        if len(j3) == 0:
            continue
        else:
            print(l)


if all_endpoints_2nd_lvl:
    print("Endpoints 2nd level:\n")
    all_endpoints_2nd_lvl_original = []  ## deleting dupes
    deduplication(all_endpoints_2nd_lvl, all_endpoints_2nd_lvl_original)
    for l in all_endpoints_2nd_lvl_original:  ## printing a lists
        if "[]" in l:
            continue
        else:
            print(l)

        ## retire js check performing using os.system

#if os.path.exists(directory_with_js_files) is True:
    #os.system("retire %s" % directory_with_js_files)

## Deleting duplicates from the js files 2nd level

## Deleting duplicates from the endpoints 1st level

## Deleting duplicates from the js files 3rdnd level

## Deleting duplicates from the endpoints 2nd level
