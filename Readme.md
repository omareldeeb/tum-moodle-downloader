# TUM Moodle Downloader
*A python-built web crawler to automate file downloads off of
https://www.moodle.tum.de/*

Prerequisites
---
* [Python](https://www.python.org/) (>= 3.4) including `pip` installed and available via the command line.

Requirements
---
* Python requirements as specified in requirements.txt.
To install all requirements run:  
`$ pip3 install -r requirements.txt`
* Note: use `pip` instead of `pip3` on Windows.

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
for general help on how to use the program
* run  
`$ python3 src/main.py list -h`  
for help concerning the `list` command
* run  
`$ python3 src/main.py download -h`  
for help concerning the `download` command
* Note:
    * Upon running one of the commands you will be prompted to enter your Moodle credentials.
    The username will be stored in a `config.json` in the `src` directory.
    _You may also manually add your password to the `config.json`, if you don't want to type it every time you run the script.
    This is discouraged though as your password will be stored in **plain text**!_
    * Use `python` instead of `python3` on Windows.

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
