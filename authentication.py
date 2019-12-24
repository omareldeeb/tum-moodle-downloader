from getpass import getpass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import requests

AUTH_LINK = 'https://www.moodle.tum.de/Shibboleth.sso/Login?providerId=https%3A%2F%2Ftumidp.lrz.de%2Fidp%2Fshibboleth' \
            '&target=https%3A%2F%2Fwww.moodle.tum.de%2Fauth%2Fshibboleth%2Findex.php '
CHROME_PATH = r'chrome/Chrome.app/Contents/MacOS/Google Chrome'
DRIVER_PATH = r'chrome/chromedriver'

chrome_options = Options()
chrome_options.binary_location = CHROME_PATH
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)

session = requests.Session()


def start_session():
    print('Starting Moodle session...')
    driver.get(AUTH_LINK)
    username = input('Enter username or email (e.g. go42tum/example@tum.de)\n')
    driver.find_element_by_id('username').send_keys(username)
    password = getpass('Password for ' + username + '\n')
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_name('_eventId_proceed').click()

    save_cookies(driver.get_cookies())
    driver.get(r'https://www.moodle.tum.de/my/')
    return driver


def save_cookies(cookies):
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
