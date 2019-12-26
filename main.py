import json
import os
from getpass import getpass


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
    import course_retrieval  # import only valid after setting up environment
    course = course_retrieval.get_course('Analysis')
    course.download_resource('Hausaufgabe 9')
