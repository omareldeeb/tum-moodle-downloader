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
    if os.path.isfile('config.json'):
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            try:
                os.environ['USERNAME'] = config_data['username']
                os.environ['PASSWORD'] = config_data['password']
                os.environ['SEMESTER'] = config_data['semester']
            except KeyError:
                print('Check config.json file')
                exit()
    else:
        print('config.json file not found. Setting up new config.json file...')
        config_data = {
            "username": input('Enter username or email (e.g. go42tum/example@tum.de)\n'),
            "password": getpass('Enter password: '),
            "semester": input('Enter semester in "YEAR-TERM" format. '
                              'e.g. "2019-2" for Winter Semester 2019/2020 or "2018-1" for Summer Semester 2018\n')
        }
        os.environ['USERNAME'] = config_data['username']
        os.environ['PASSWORD'] = config_data['password']
        os.environ['SEMESTER'] = config_data['semester']
        config_json = json.dumps(config_data)
        with open('config.json', 'w') as f:
            f.write(config_json)


if __name__ == "__main__":
    setup_env()
    session = authentication.start_session(
        os.environ['USERNAME'],
        os.environ['USERNAME']
    )

    course = course_retrieval.get_course(session, 'anal')
    print(course)
    # import course_retrieval  # import only valid after setting up environment
    # download_args = get_download_arguments()
    # course_name = download_args.course
    # file = os.path.expanduser(download_args.file)
    # path = os.path.expanduser(download_args.path)
    #
    # course = course_retrieval.get_course(course_name)
    # course.download_resource(file, path)
    #
    # course_retrieval.container.stop()
