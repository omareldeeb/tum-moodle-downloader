import json
import re

from globals import DOWNLOAD_CONFIG_PATH
import course_retrieval


def list_resources(args, session):
    course_name = args.course
    if course_name == "*":
        print('Listing available courses: ')
        course_retrieval.list_courses(session)
        exit(0)

    course = course_retrieval.get_course(session, course_name)
    if course_name is not None and course is None:
        exit(1)
    else:
        course.list_all_resources()
        exit(0)


def download(args, session):
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

    with open(DOWNLOAD_CONFIG_PATH, mode='r', encoding='utf-8') as json_file:
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