# TUM Moodle Downloader
*A python-built web crawler to automate file downloads off of
https://www.moodle.tum.de/*

Requirements
---
* Python requirements as specified in requirements.txt.
To install all requirements run:

    `$ pip3 install -r requirements.txt`
* [Docker](https://www.docker.com/get-started) for remote access
to Selenium Webdriver that powers this crawler.

Quick Start
---
*Assuming Docker is installed,*

* Run `$ docker run -d -p 4444:4444 selenium/standalone-chrome` to 
start the container with the required webdriver.

* Then, run
`$ python3 src/main.py -c COURSE -f FILE [-p PATH]` to
download the specified `FILE` from the specified `COURSE` into the
specified `PATH`
    * _Running for the first time will prompt user for TUM Moodle
    credentials and semester and store them in a config.json file_


* Lastly, run `$ docker stop $(docker ps -qf "name=zealous_edison")`
to stop the running container and (*optional*) `$ docker system prune` to
remove **all** stopped containers. 