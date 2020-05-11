# TUM Moodle Downloader
*A python-built web crawler to automate file downloads off of
https://www.moodle.tum.de/*

Prerequisites
---
* [Python](https://www.python.org/) (>= 3.4) including `pip` installed and available via the command line.

Setup
---
* Clone or download this repository to your local file system.
* Install all Python requirements specified in `requirements.txt` by running  
`$ pip3 install -r requirements.txt`  
from the projects directory.  
Note: use `pip` instead of `pip3` on Windows

Quick Start
---
* run  
`$ python3 src/main.py download`  
to download resources from Moodle based on 
your configuration in `src/download_config.json` 
(see the section below for more information on the configuration)
* run  
`$ python3 src/main.py download course`  
to download resources from the specified Moodle course based on 
your configuration in `src/download_config.json`
* run  
`$ python3 src/main.py download course file_pattern destination`  
to
download resources which match the `file_pattern` from `course` to a `destination` path
* run  
`$ python3 src/main.py list [course]`
to list available resources of the specified `course` or, if no course is specified, list available courses for your
Moodle account
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
    _You may also manually add your password to the `config.json`, 
    if you don't want to type it every time you run the script.
    This is discouraged though as your password will be stored in **plain text**!_
    * Use `python` or `py` instead of `python3` on Windows.

Configuration
---
You can configure from which courses which files should be downloaded and
where they should be stored by editing the file `download_config.json` in the `src` directory. Additionally you can
specify what should happen, if the file which is to be downloaded already exists at the specified destination path.
How the configuration works shall be explained via the following example:
* Example contents of `download_config.json`:
```json
[
  {
    "course_name": "Analysis für Informatik",
    "semester": "WS19_20",
    "rules": [
      {
        "file_pattern": "Hausaufgabe.*",
        "destination": "C:\\Users\\yourusername\\Documents\\Uni\\Analysis\\Hausaufgaben",
        "update_handling": "replace"
      },
      {
        "file_pattern": ".*E-Test.*",
        "destination": "C:\\Users\\yourusername\\Documents\\Uni\\Analysis\\E-Tests",
        "update_handling": "skip"
      }
    ]
  },
  {
    "course_name": "Numerisches Programmieren",
    "semester": "WS19_20",
    "rules": [
      {
        "file_pattern": "(Übungsblatt.*|Musterlösung Blatt.*)",
        "destination": "C:\\Users\\yourusername\\Documents\\Uni\\NumProg\\Übungen\\",
        "update_handling": "add"
      }
    ]
  }
]
```
* Upon running `$ python3 src/main.py download` the program goes through the configuration objects for the different
courses one by one. For each course all available resources are checked against the rules specified for the course. 
If a resource name matches a pattern specified in one of the rules, the resource is downloaded to the destination path
defined by that rule (no other rules are applied to that resource afterwards). If the resource already exists locally, 
the specified `update_handling` is applied.
* In the example at hand all resources of the course "Analysis für Informatik [MA0902]" of which the name starts with 
"Hausaufgabe" are downloaded to the folder "C:\Users\yourusername\Documents\Uni\Analysis\Hausaufgaben". 
If the respective file already exists, it is replaced in this case.
Resources of which the name contains "E-Test" will be downloaded the destination defined by the respective rule.
In this case the download is skipped, if the file already exists.
Resources of the course "Numerisches Programmieren (IN0019)" which either start with "Übungsblatt" 
or with "Musterlösung Blatt" will be downloaded to "C:\Users\yourusername\Documents\Uni\NumProg\Übungen".
Here a new version of the file is added (e.g. Übungsblatt 12 (1).pdf), if the file
already exists at the specified destination.
* Important: resources from courses which are not listed in the configuration file or resources for which none of the
rules apply are not downloaded.
* Options for the `update_handling` are:
    * "skip" --> the download is skipped, if the file already exists locally
    * "replace" --> existing local files are simply overridden by the download 
    * "add" --> a new version in the form "filename (versionnumber).extension" is added to the specified `destination`,
    if the file already exists locally
    * If nothing is specified for the `update_handling`, existing local files are overridden
* Note:
    * Running `$ python3 src/main.py download "Analysis für Informatik"` downloads only the resources for the course
    "Analyis für Informatik" based on the configuration file.
    * Use `".*"` as the pattern for the last rule, if you want files for which none of the other rules apply to be
    downloaded.
    * The pattern matching is based on [Regular Expressions aka regex](https://en.wikipedia.org/wiki/Regular_expression)
    * The course name only needs to be a substring of the full course name. If multiple of your Moodle courses match the
    specified course name, currently only the first one that is found will be taken into account.
    * Currently the value specified for the semester is not used.


Examples
---
* For an example which downloads resources based on the configuration file see the section above.
* `$ python3 src/main.py list "Analysis für Informatik"` 
will list all resources of the course `Analysis für Informatik` available for download.

* `$ python3 src/main.py download "Analysis für Informatik" "Hausaufgabe 10" "~/Documents/Uni/WS19/Analysis/Hausaufgaben"` 
will search the user's courses for `Analysis für Informatik`
and find a matching course (e.g. "Analysis für Informatik [MA0902]"). In this example, the script
will search for `Hausaufgabe 10` and find the assignment "Hausaufgabe 10 und Präsenzaufgaben der Woche".
The script will then navigate to the assignment's page and download the associated file: "Blatt10.pdf", which
will then be saved in the specified path `~/Documents/Uni/WS19/Analysis/Hausaufgaben`.

* `$ python3 src/main.py downlaod "Analysis für Informatik" "Hausaufgabe.*" "~/Documents/Uni/WS19/Analysis/Hausaufgaben"`  
similar to above, however, finds multiple files that start with `Hausaufgabe` and downloads
them **all**.
