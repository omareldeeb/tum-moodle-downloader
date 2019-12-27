from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests

AUTH_LINK = 'https://www.moodle.tum.de/Shibboleth.sso/Login?providerId=https%3A%2F%2Ftumidp.lrz.de%2Fidp%2Fshibboleth' \
            '&target=https%3A%2F%2Fwww.moodle.tum.de%2Fauth%2Fshibboleth%2Findex.php '
try:
    driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
except:
    print('Could not establish connection to remote webdriver. Please make sure to have docker installed and run: '
          'docker run -d -p 4444:4444 selenium/standalone-chrome before running the moodle downloader.')
    exit()
session = requests.Session()


def start_session(username, password):
    print('Starting Moodle session...')
    driver.get(AUTH_LINK)
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_name('_eventId_proceed').click()

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
