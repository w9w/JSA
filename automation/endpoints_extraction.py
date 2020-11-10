#!/usr/bin/env python3
import re
import requests
import io
import sys
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tld_detection import tld_detection


js_file = sys.stdin.readlines()

# js_file = open("/Users/max/test13.txt", "r").readlines()


## just some containers for future values

original_lines = []

all_endpoints_1st_lvl = []
all_endpoints_original = []
js_files_2nd_lvl = []


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


def main_func(original_lines, all_endpoints):
    for line in original_lines:  ## main loop

        clear_url0 = re.findall("^(.*?)\\b/", line)
        global clear_url
        clear_url = re.sub("\['|'\]", "", str(clear_url0))  ## matching URL without js part
        domain_name = tld_detection(clear_url)
        if "[]" in clear_url:
            continue
        warnings.simplefilter('ignore', InsecureRequestWarning)
        js_file_status = requests.head(line,
                                       verify=False).status_code  ## fastly (HEAD) finding out a status code of js file url
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
                if not re.findall("\.js$", one):
                    all_endpoints.append(one)  ## printing 1st lvl endpoints
        ##elif js_file_status == 404 and verbose is True:  ## todo make it for subjs output only
            ##print("JS file {} returned 404 code. Check the host and try to apply file upload with path traversal/PUT method file upload.".format(line))


deduplication(js_file, original_lines)
main_func(original_lines, all_endpoints_1st_lvl)

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

# if os.path.exists(directory_with_js_files) is True:
# os.system("retire %s" % directory_with_js_files)
