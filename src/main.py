import json
import os
from getpass import getpass
import argparse
import authentication
import course_retrieval


def get_download_arguments():
    ap = argparse.ArgumentParser(description='Automatically download files, folders and assignment material from TUM '
                                             'Moodle')
    ap.add_argument(
        '-c',
        '--course',
        dest='course',
        metavar='COURSE',
        type=str,
        required=True,
        help='Course to download material from.'
    )
    ap.add_argument(
        '-f',
        '--file',
        dest='file',
        type=str,
        required=True,
        help='File to download'
    )
    ap.add_argument(
        '-p',
        '--path',
        dest='path',
        type=str,
        required=False,
        default='./',
        help='Path to save downloaded resource. (Default: current directory)'
    )
    return ap.parse_args()


def setup_env():
    if os.path.isfile('credentials.json'):
        with open('credentials.json', 'r') as f:
            config_data = json.load(f)
            try:
                os.environ['USERNAME'] = config_data['username']
                os.environ['PASSWORD'] = config_data['password']
            except KeyError:
                print('Check credentials.json file')
                exit()
    else:
        print('credentials.json file not found. Setting up new credentials.json file...')
        config_data = {
            "username": input('Enter username or email (e.g. go42tum/example@tum.de)\n'),
            "password": getpass('Enter password: '),
        }
        os.environ['USERNAME'] = config_data['username']
        os.environ['PASSWORD'] = config_data['password']
        config_json = json.dumps(config_data)
        with open('credentials.json', 'w') as f:
            f.write(config_json)


if __name__ == "__main__":
    setup_env()
    session = authentication.start_session(
        os.environ['USERNAME'],
        os.environ['PASSWORD']
    )

    # print(course)
    download_args = get_download_arguments()
    course_name = download_args.course
    file = os.path.expanduser(download_args.file)
    path = os.path.expanduser(download_args.path)

    course = course_retrieval.get_course(session, course_name)
    course.download_resource(file, path)
