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
`$ python3 src/main.py download course file [destination]`  
to
download `file`(s) from a `course` into a `destination` path
* run  
`$ python3 src/main.py list [course]`
to list available resources of the specified `course` or, if no course is specified, list available courses
* run
`$ python3 src/main.py -h`
for general help
* run
`$ python3 src/main.py list -h`
for help concerning the `list` command
* run
`$ python3 src/main.py download -h`
for help concerning the `download` command
* Note:
    * _Running for the first time will prompt user for TUM Moodle
    credentials and semester and store them in a credentials.json file_
    * Use `python` instead of `python3` on Windows

Examples
---
* `$ python3 src/main.py list "Analysis für Informatik"` 
will list all resources of the course `Analysis für Informatik` available for download.

* `$ python3 src/main.py download "Analysis für Informatik" "Hausaufgabe 10" "~/Documents/Uni/WS19/Analysis/Hausaufgaben"` 
will search the user's courses for `Analysis für Informatik`
and find a matching course (e.g. "Analysis für Informatik [MA0902]"). In this example, the script
will search for `Hausaufgabe 10` and find the assignment "Hausaufgabe 10 und Präsenzaufgaben der Woche".
The script will then navigate to the assignment's page and download the associated file: "Blatt10.pdf", which
will then be saved in the specified path `~/Documents/Uni/WS19/Analysis/Hausaufgaben`.

* `$ python3 src/main.py downlaod "Analysis für Informatik" "Hausaufgabe" "~/Documents/Uni/WS19/Analysis/Hausaufgaben"`  
similar to above, however, finds multiple files that match `Hausaufgabe` and downloads
them **all**.
