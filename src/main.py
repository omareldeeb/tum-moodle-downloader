import json
import os
import sys
import argparse
from pathlib import Path
from getpass import getpass
import json
import re

import authentication
import course_retrieval

# Build path relative to absolute path of script (or rather the scripts parent dir)
# Source: https://stackoverflow.com/a/55051039
BASE_PATH = Path(__file__).parent
CREDENTIALS_PATH = (BASE_PATH / "./credentials.json").resolve()
CONFIG_PATH = (BASE_PATH / "./download_config.json").resolve()


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
    print(args)
    course_name = args.course
    resource_pattern = args.file_pattern
    destination_path = args.destination

    if destination_path is None:
        if resource_pattern is None:
            resource_pattern = ".*"
        if course_name is None:
            course_name = ".*"
        download_via_config(session, course_name, resource_pattern)
    else:
        course = course_retrieval.get_course(session, course_name)

        resource_names = course.get_matching_resource_names(resource_pattern)
        for resource_name in resource_names:
            course.download_resource(resource_name, destination_path, update_handling="replace")


def download_via_config(session, req_course_name=".*", req_file_pattern=".*"):
    print("Downloading via download config ...")

    # TODO: check if requested file course name and requested file pattern exist in the config file
    req_course_name = re.compile(req_course_name)
    req_file_pattern = re.compile(req_file_pattern)

    with open(CONFIG_PATH, mode='r', encoding='utf-8') as json_file:
        config_data = json.load(json_file)

    for course_config in config_data:
        course_name = course_config.get('course_name', None)
        if not re.match(req_course_name, course_name):
            continue

        semester = course_config.get('semester', None)
        rules = course_config.get('rules', [])

        course = course_retrieval.get_course(session, course_name)
        if course is None:
            continue

        resource_names = course.get_matching_resource_names()
        for resource_name in resource_names:
            if not re.match(req_file_pattern, resource_name):
                continue
            for rule in rules:
                file_pattern = re.compile(rule.get('file_pattern', None))
                destination = rule.get('destination', None)
                update_handling = rule.get('update_handling', "replace")
                if re.match(file_pattern, resource_name):
                    course.download_resource(resource_name, destination, update_handling)
                    break
    print("Done downloading via download config.")


if __name__ == "__main__":
    # Instantiate the argument parser
    arg_parser = argparse.ArgumentParser()

    # Add subparsers for the different available commands
    subparsers = arg_parser.add_subparsers()

    list_command_description = "List available resources of the specified 'course' " \
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

    download_command_description = "Download resources which match a 'file_pattern' " \
                                   "from a 'course' into a 'destination' path. " \
                                   "If parameters are omitted they are retrieved from  'src/download_config.json'"
    download_parser = subparsers.add_parser("download",
                                            description=download_command_description,
                                            help=download_command_description)
    download_parser.add_argument('course',
                                 type=str,
                                 nargs='?',
                                 help="name of the course from which to download")
    download_parser.add_argument('file_pattern',
                                 type=str,
                                 nargs='?',
                                 help="name pattern for the resources which are to be downloaded")
    download_parser.add_argument('destination',
                                 type=str,
                                 nargs='?',
                                 help="path at which the download(s) should be stored")
    # Set the function which is to be executed, if the 'download' command is provided
    download_parser.set_defaults(func=download)

    args = arg_parser.parse_args()

    username, password = get_credentials()
    session = authentication.start_session(
        username,
        password
    )
    if session is None:
        print('Could not start session.')
        exit(1)

    # Call the function which is set based on the command provided in the arguments (see above for details)
    args.func(args, session)
