import os
import json
from getpass import getpass

from .globals import CREDENTIALS_PATH


def get_credentials():
    username = None
    password = None
    if os.path.isfile(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, 'r') as f:
            config_data = json.load(f)
            username = config_data.get("username", None)
            password = config_data.get("password", None)
    if username is None:
        username = input("Enter username or email (e.g. go42tum or example@tum.de): ")
        config_data = {
            "username": username,
            "password": None,
        }
        print(f'Saving user name in {CREDENTIALS_PATH} ...')
        with open(CREDENTIALS_PATH, 'w') as f:
            json.dump(config_data, f)
    if password is None:
        password = getpass(f'Enter password for {username}: ')

    return username, password
