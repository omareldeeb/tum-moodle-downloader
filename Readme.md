# TUM Moodle Downloader
*A python-built web crawler to automate file downloads off of
https://www.moodle.tum.de/*

Requirements
---
* Python requirements as specified in requirements.txt.
To install all requirements run:

    `$ pip3 install -r requirements.txt`

Quick Start
---

* run  
`$ python3 src/main.py -c COURSE -f FILE [-p PATH]`  
to
download the specified `FILE` from the specified `COURSE` into the
specified `PATH`
    * _Running for the first time will prompt user for TUM Moodle
    credentials and semester and store them in a credentials.json file_

Examples
---
* `$ python3 src/main.py -c 'Analysis' -f 'Hausaufgabe 10' -p '~/Documents/Uni/WS19/Analysis/Hausaufgaben'`  
will search the user's courses for `'Analysis'`
and find the course 'Analysis für Informatik [MA0902]'. In this example, the script
will search for `'Hausaufgabe 10'` and find the assignment 'Hausaufgabe 10 und Präsenzaufgaben der Woche'.
The script will then navigate to the assignment's page and download the associated file: 'Blatt10.pdf', which
will then be saved in the specified path `'~/Documents/Uni/WS19/Analysis/Hausaufgaben'`.

* `$ python3 src/main.py -c 'Analysis' -f 'Hausaufgabe' -p '~/Documents/Uni/WS19/Analysis/Hausaufgaben'`  
similar to above, however, finds multiple files that match `'Hausaufgabe'` and downloads
them **all**.
