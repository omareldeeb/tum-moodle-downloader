import requests
from bs4 import BeautifulSoup

AUTH_URL = 'https://www.moodle.tum.de/auth/shibboleth/index.php'
IDP_BASE_URL = 'https://tumidp.lrz.de/'

proxies = {
    # 'http': 'localhost:8080',
    # 'https': 'localhost:8080',
}
headers = {
    'user-agent': 'Mozilla/5.0',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
}


def _find_action_url(soup) -> str or None:
    content_div = soup.find('div', {'id': 'content'})
    form = content_div.find('form')
    if not form:
        return None
    return form.get('action', None)


def _find_sso_data(soup) -> (str, dict) or None:
    form = soup.find('form')
    action_url = form.get('action')
    form_div = form.find('div')
    if not form_div:
        return None
    sso_headers = {}
    inputs = form_div.find_all('input')
    for form_input in inputs:
        sso_headers[form_input.get('name')] = form_input.get('value')
    return action_url, sso_headers


def start_session(username, password) -> requests.Session or None:
    print('Starting Moodle session...')
    session = requests.Session()
    response = session.get(
        AUTH_URL,
        proxies=proxies,
        verify=True,
    )

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    action_url = _find_action_url(soup)
    if not action_url:
        print('error while starting session: could not find action url')
        return None

    response = session.post(
        f'{IDP_BASE_URL}{action_url}',
        headers=headers,
        data={
            'j_username': username,
            'j_password': password,
            'donotcache': '1',
            '_eventId_proceed': '',
        },
        proxies=proxies,
        verify=True,
    )
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    action_url, sso_data = _find_sso_data(soup)
    try:
        response = session.post(
            f'{action_url}',
            headers=headers,
            data=sso_data
        )
    except requests.exceptions.MissingSchema:
        print('Error while authenticating. Check credentials.')
        return None
    if response.status_code == 200:
        return session
    return None
