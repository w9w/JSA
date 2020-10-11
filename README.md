# What the tool can do:

- Firstly, it modifies found endpoins in the javascript file from /endpoint to http(s)://host_from_js_file.com/endpoint. This is a very usefull approach when you have a huge list of javascript files and would like to verify affiliation to specified host. It makes massive javascript files check easy.
- Look for js files inside the first and second level js files. For example, http(s)://host.com/file.js contains a string "//host.com/file.js" which could be different from already known 1st level js files and contain additional endpoints or secrets.
- Display endpoints for the second level js files.
- Exclude and print 3rd party js files like https://googleapis.com or //facebook.net (most likely 2nd level js file) to reduce script runtime and remove unnecessary endpoints. Also, it is usefull to identify 3rd party js files since we can expande our attack surface and attack a 3rd party website to try to make change to the javascript file.
- Remove duplicates - js files and endpoints. By default, most of the tools for js grabbing (like subjs, gau, etc) can provide a list of js files containing duplicates. Even if they performed deduplication procedure, a list can still contain duplicates since, for example, http(s)://host.com/file.js and http(s)://host.com/file.js?identifier=random_str are the same js files. Deleting duplicates can greatly boost the program's performance.
- Remove unnecessary files with such extensions .css|.png|.jpg|.svg|.jpeg|.ico|.gif|.woff|.woff2|.swf.
- Check the http code of the js file using HEAD method (it's faster than just GET). If 200 - it goes for further processing (because all js files should have a 200 code, otherwise there will be no loading on the page), if 404 - then such a code indicates a non-existing file (or an unregistered host with a file) that can be uploaded by an attacker for the displaying on the page.


Roadmap:
- replace [] // with http (s) host.tld /, if they exist;
- deletion of duplicate files of the second level in relation to the files of the first level;
- setting the js file in the parameter when calling the program, still saving stdin;
- set multiple js files in the parameter as a tuple, still saving stdin;
- output the second level files **optionally**, by parameter;
- save all found endpoints to a file **optionally**, by parameter;
- improve the exclusion of 3rd party scripts by domain for multiple domains during bulk scanning, if possible;
- define domain and tld using re depending on line, if it's possible;
- check available HTTP methods for endpoints;
- retire js check via downloading js files to the temporary directory using wget;
- credentials leak check using secretfinder.py with extended regular expressions;
- brute-forcing parameters for endpoints using arjun.py;
- make a file with endpoints along with parameters for pipelining to check for XSS'es, CORS misconfigs, etc.
