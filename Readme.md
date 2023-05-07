# TUM Moodle Complete Backup Tool

### A [fork of python-built web crawler](https://github.com/omareldeeb/tum-moodle-downloader) to completely backup all files of [TUM Moodle](https://www.moodle.tum.de/)
---

Prerequisites
---

* [Python](https://www.python.org/) (>= 3.9) including `pip` installed and available via the command line.

Setup
---

* Clone or download this repository to your local file system.
* Install all Python requirements specified in `requirements.txt` by running  
  `$ pip install -r requirements.txt`  
  from the projects directory.  
  Note: use `pip3`, if `pip` is linked to `python 2.x`
  and same for `python/3`

Quick Start
---

* First open `src/main.py` on line 86 and set the path where the files should be downloaded to.
* Then type `$ python3 src/main.py`.
* You will be prompted to log in with your TUM Account. 
* After the log in all your Moodle files will be downloaded.

Big Thanks to
---

[Omar Eldeeb](https://github.com/omareldeeb/tum-moodle-downloader) who did all the hard work!