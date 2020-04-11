import json
import os
import sys
import argparse
from getpass import getpass


import authentication
import course_retrieval


def setup_credentials():
    credentials_path = os.path.join(sys.path[0], 'credentials.json')
    if os.path.isfile(credentials_path):
        with open(credentials_path, 'r') as f:
            config_data = json.load(f)
            try:
                os.environ['USERNAME'] = config_data['username']
                os.environ['PASSWORD'] = config_data['password']
            except KeyError:
                print('Check credentials.json file')
                exit(1)
    else:
        print('credentials.json file not found. Setting up new credentials.json file...')
        config_data = {
            "username": input('Enter username or email (e.g. go42tum/example@tum.de)\n'),
            "password": getpass('Enter password: '),
        }
        os.environ['USERNAME'] = config_data['username']
        os.environ['PASSWORD'] = config_data['password']
        config_json = json.dumps(config_data)
        with open(credentials_path, 'w') as f:
            f.write(config_json)


def list_resources(args, session):
    course_name = args.course
    if course_name == "*":
        print('Listing available courses: ')
        course_retrieval.list_courses(session)
        exit(0)

    course = course_retrieval.get_course(session, course_name)
    if course_name is not None and course is None:
        print('Could not find course: ' + course_name)
        exit(1)
    else:
        course.list_all_resources()
        exit(0)


def download(args, session):
    course_name = args.course
    file_name = args.file
    destination_path = args.destination
    course = course_retrieval.get_course(session, course_name)

    course.download_resource(file_name, destination_path)


if __name__ == "__main__":
    # Instantiate the argument parser
    arg_parser = argparse.ArgumentParser()

    # Add subparsers for the different available commands
    subparsers = arg_parser.add_subparsers()

    list_command_description = "list available resources of the specified 'course' " \
                               "or, if no course is specified, list available courses"
    list_parser = subparsers.add_parser("list",
                                        description=list_command_description,
                                        help=list_command_description)
    list_parser.add_argument("course",
                             type=str,
                             nargs='?',
                             default='*',
                             help="name of the course of which the resources are to be listed")
    # Set the function which is to be executed, if the 'list' command is provided
    list_parser.set_defaults(func=list_resources)

    download_command_description = "download 'file'(s) from a 'course' into a 'destination' path"
    download_parser = subparsers.add_parser("download",
                                            description=download_command_description,
                                            help=download_command_description,
                                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    download_parser.add_argument('course',
                                 type=str,
                                 help="name of the course from which to download")
    download_parser.add_argument('file',
                                 type=str,
                                 help="name pattern for the files which are to be downloaded")
    download_parser.add_argument('destination',
                                 type=str,
                                 nargs='?',
                                 default='./moodle_downloads/',
                                 help="path at which the download(s) should be stored")
    # Set the function which is to be executed, if the 'download' command is provided
    download_parser.set_defaults(func=download)

    args = arg_parser.parse_args()

    setup_credentials()
    session = authentication.start_session(
        os.environ['USERNAME'],
        os.environ['PASSWORD']
    )
    if session is None:
        print('Could not start session.')
        exit(1)

    # Call the function which is set based on the command provided in the arguments (see above for details)
    args.func(args, session)
