import requests

from bs4 import BeautifulSoup

AUTH_URL = 'https://www.moodle.tum.de/Shibboleth.sso/Login?providerId=https://tumidp.lrz.de/idp/shibboleth&target' \
           '=https://www.moodle.tum.de/auth/shibboleth/index.php'
IDP_BASE_URL = 'https://login.tum.de'

proxies = {
    # 'http': 'localhost:8080',
    # 'https': 'localhost:8080',
}

base_headers = {
    'user-agent': 'Mozilla/5.0',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

additional_headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}


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
    print('Starting Moodle session')
    session = requests.Session()
    session.headers.update(base_headers)

    response = session.get(
        AUTH_URL,
        proxies=proxies,
        verify=True,
        allow_redirects=False
    )
    if response.status_code != 302:
        print(f"Error while starting session: request to {AUTH_URL} didn't redirect")
        return None

    saml_url = response.headers.get('Location')
    if not saml_url:
        print("Error while starting session: could not find SAML url")
        return None

    response = session.get(
        saml_url,
        verify=True,
        allow_redirects=False
    )

    sso_url = response.headers.get('Location')
    if not sso_url:
        print("Error while starting session: could not find SSO url")
        return None

    response = session.post(
        f'{IDP_BASE_URL}{sso_url}',
        headers=additional_headers,
        proxies=proxies,
        verify=True,
    )

    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find("input").attrs['value']

    response = session.post(
        f'{IDP_BASE_URL}{sso_url}',
        headers=additional_headers,
        data={
            'csrf_token': csrf_token,
            'j_username': username,
            'j_password': password,
            'donotcache': '1',
            '_eventId_proceed': '',
        },
        proxies=proxies,
        verify=True,
    )
    if response.status_code != 200:
        print(f"Error while starting session: request to SSO url failed")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    action_url, sso_data = _find_sso_data(soup)
    try:
        response = session.post(
            f'{action_url}',
            headers=additional_headers,
            data=sso_data
        )
    except requests.exceptions.MissingSchema:
        print('Error while authenticating. Check credentials.')
        return None

    if response.status_code != 200:
        print(f"Error while starting session: login failed")
        return None

    return session
