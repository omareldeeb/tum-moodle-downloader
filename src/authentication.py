from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
import requests
import docker
import time


AUTH_LINK = 'https://www.moodle.tum.de/Shibboleth.sso/Login?providerId=https%3A%2F%2Ftumidp.lrz.de%2Fidp%2Fshibboleth' \
            '&target=https%3A%2F%2Fwww.moodle.tum.de%2Fauth%2Fshibboleth%2Findex.php '


def _start_container():
    cont = None
    client = docker.from_env()
    ports = {'4444': '4444'}
    print('Starting container...')
    try:
        cont = client.containers.run('selenium/standalone-chrome:latest', ports=ports, detach=True, remove=True)
        time.sleep(2)
    except docker.errors.APIError:
        print('Container already running.')
    except requests.exceptions.ConnectionError:
        print('Could not start container. Please make sure Docker is installed and running.')
        exit()

    return cont


container = _start_container()

try:
    driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
except:
    print('Could not establish connection to remote webdriver. Please try again.')
    exit()
session = requests.Session()


def start_session(username, password):
    print('Starting Moodle session...')
    try:
        driver.get(AUTH_LINK)
        driver.find_element_by_id('username').send_keys(username)
        driver.find_element_by_id('password').send_keys(password)
        driver.find_element_by_name('_eventId_proceed').click()
    except WebDriverException:
        print('Webdriver crashed unexpectedly. Try restarting the docker container.')
        exit()

    save_cookies(driver.get_cookies())
    driver.get('https://www.moodle.tum.de/my/')
    if driver.current_url != 'https://www.moodle.tum.de/my/':
        print('Authentication failed. Please check your credentials.')
        exit()
    print('authentication successful')
    return driver, session


def save_cookies(cookies):
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
