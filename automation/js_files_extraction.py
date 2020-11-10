import re
import requests
import io
import sys
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tld_detection import tld_detection

js_file = sys.stdin.readlines()


original_lines = []
js_files_2nd_lvl = []
js_files_3rd_lvl = []
js_files_4th_lvl = []

js_files_3rd_lvl_original = []
tmp_list = []

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

clear_url_global = []

def main_func(original_lines, js_files):
    for line in original_lines:  ## main loop

        # tld = re.sub("^[a-z]+\.", "", domain_name)              ## matching TLD

        clear_url0 = re.findall("^(.*?)\\b/", line)
        global clear_url
        clear_url = re.sub("\['|'\]", "", str(clear_url0))  ## matching URL without js part
        domain_name = tld_detection(clear_url)
        if "[]" in clear_url:
            continue
        ##if str(domain_name) not in str(line):     ## deleting since this is automation and we need a clear output
        ## excluding 3rd party js files & print 'em
        # print("3rd party JS file has been found: " + line)
        # continue
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
                u = re.sub("^//(.*?)/", clear_url + "/", u, flags=re.M)
            else:
                u = re.sub("^", clear_url, u, flags=re.M)
            u_lines = io.StringIO(u).readlines()  ## endpoints

            for one in u_lines:
                if re.findall("\.js$", one):
                    ##if re.findall("^//", one) and verbose is True:  ## excluding 3rd party 2nd lvl js files & print 'em
                    ##print("3rd party JS file has been found: " + one)                         ## deleting since this is automation and we need a clear output
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
        ##elif js_file_status == 404:  ## todo make it for subjs output only          ## deleting since this is automation and we need a clear output
        # print(
        # "JS file {} returned 404 code. Check the host and try to apply file upload with path traversal/PUT method file upload.".format(line))


deduplication(js_file, original_lines)

main_func(original_lines, js_files_2nd_lvl)

if len(js_files_2nd_lvl) != 0:  ## processing 2nd level js files
    ##if verbose is True:               ## deleting since this is automation and we need a clear output
        ##print("\nJS files 2nd level:\n")
    js_files_2nd_lvl_original = []
    deduplication(js_files_2nd_lvl, js_files_2nd_lvl_original)  ## removing dupes
    for l in js_files_2nd_lvl_original:  ## printing a list
        j2 = re.findall("\.js", l)  ## sometimes (I don't know why though), non-js files leak to the list
        if len(j2) == 0:
            continue
        elif l not in original_lines:
            print(l)
    main_func(js_files_2nd_lvl_original, js_files_3rd_lvl)

if len(js_files_3rd_lvl) != 0:
    ##if verbose is True:
        ##print("JS files 3rd level:\n")
    deduplication(js_files_3rd_lvl, js_files_3rd_lvl_original)  ## removing dupes
    for l in js_files_3rd_lvl_original:  ## printing a list
        j3 = re.findall("\.js$", l)  ## sometimes (I don't know why though), non-js files leak to the list
        if len(j3) == 0:
            continue
        elif l not in js_files_2nd_lvl_original and original_lines:
            if re.findall("^htt(p|s)(.*?)\w//(.*?)/", l):
                l = re.sub("^htt(p|s)(.*?)\w//(.*?)/", clear_url + "/", l, flags=re.M)
                tmp_list.append(l)
                print(l)
    js_files_3rd_lvl_original.clear()
    js_files_3rd_lvl_original = tmp_list

    #main_func(js_files_3rd_lvl, js_files_4th_lvl)

