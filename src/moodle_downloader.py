import json
import re

import globals
import course_retrieval

import argparse


def list_resources(args):
    try:
        course_name = args.course
        if course_name == "*":
            # List the names of all available courses
            courses_list = course_retrieval.list_courses()
            return courses_list
        else:
            # List all available resources within the specified course
            course = course_retrieval.get_course(course_name)
            if course is not None:
                if args.files:
                    course.list_all_files()
                else:
                    course.list_all_resources()
    except:
        # TODO: add logging and log exception info (traceback) to a file
        print("Could not list resources due to an internal error.")
        

def complete_backup(args):
    destination = args.destination
    # 1) Finds all courses and saves them in a list
    args = argparse.Namespace(course = "*")
    courses_list = list_resources(args)

    # 2) Downloads all courses
    for x in courses_list:
        path = destination + "/"  + x + "/"
        args = argparse.Namespace(course = x, file_pattern = ".*", destination = path)
        download(args)
        print("Downloaded course: " + x)
        
    print("Complete Backup finished :-)")
    

def download(args):
    try:
        course_name = args.course
        resource_pattern = args.file_pattern
        destination_path = args.destination

        if destination_path is None:
            if resource_pattern is None:
                resource_pattern = ".*"
            if course_name is None:
                course_name = ".*"
            download_via_config(course_name, resource_pattern)
        else:
            course = course_retrieval.get_course(course_name)
            resource_names = course.get_matching_resource_names(resource_pattern)

            with open(globals.DOWNLOAD_CONFIG_PATH, mode='r', encoding='utf-8') as download_config_file:
                config_data = json.load(download_config_file)[0]
                parallel = config_data.get('parallel_downloads', bool)
                if parallel:
                    print("\u001B[33mParallel downloads active! This leads to unsorted download logging\u001B[0m")
            for resource_name in resource_names:
                course.download_resource(resource_name, destination_path, parallel, update_handling="update")
    except:
        # TODO: add logging and log exception info (traceback) to a file
        print("Could not download resources due to an internal error.")


def download_via_config(req_course_name=".*", req_file_pattern=".*"):
    print("Downloading via download config")
    try:
        # TODO: check if requested file course name and requested file pattern exist in the config file
        req_course_name = re.compile(req_course_name)
        req_file_pattern = re.compile(req_file_pattern)

        with open(globals.DOWNLOAD_CONFIG_PATH, mode='r', encoding='utf-8') as download_config_file:
            download_config_data = json.load(download_config_file)[0]
            parallel = download_config_data.get('parallel_downloads', bool)
            if parallel:
                print("\u001B[33mParallel downloads active! This leads to unsorted download logging\u001B[0m")
        with open(globals.COURSE_CONFIG_PATH, mode='r', encoding='utf-8') as course_config_file:
            course_config_data = json.load(course_config_file)

        for course_config in course_config_data:
            course_name = course_config.get('course_name', None)
            if not re.match(req_course_name, course_name):
                continue

            # semester = course_config.get('semester', None)
            rules = course_config.get('rules', [])

            course = course_retrieval.get_course(course_name)
            if course is None:
                continue

            resource_names = course.get_matching_resource_names()
            for resource_name in resource_names:
                if not re.match(req_file_pattern, resource_name):
                    continue
                for rule in rules:
                    file_pattern = re.compile(rule.get('file_pattern', None))
                    if re.match(file_pattern, resource_name):
                        destination = rule.get('destination', None)
                        update_handling = rule.get('update_handling', "replace")
                        course.download_resource(resource_name, destination, parallel, update_handling)
                        break
        print("Done downloading via download config.")
    except:
        # TODO: add logging and log exception info (traceback) to a file
        print("Could not download via config due to an internal error.")
