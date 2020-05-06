import os
import re
import urllib.parse

from bs4 import BeautifulSoup

import globals
from resource import Resource


class Course:
    def __init__(self, course_name, course_url):
        self.name = course_name
        self.course_url = course_url

        self.course_page = globals.global_session.get(self.course_url).content
        self.soup = BeautifulSoup(self.course_page, 'html.parser')
        self._extract_resources()

    def _extract_resources(self):
        self.resources = {}
        self.latest_resources = []
        sections = []
        latest_week_section = None

        # Extract sections for courses structured by weeks
        weeks = self.soup.find('ul', class_='weeks')
        if weeks is not None:
            sections += weeks.find_all('li', class_='section main clearfix')  # All week secation
            latest_week_section = weeks.find('li', class_='section main clearfix current')
            if latest_week_section is not None:
                sections.append(latest_week_section)

        # Extract sections for courses structured by topics
        topics = self.soup.find('ul', class_='topics')
        if topics is not None:
            sections += topics.find_all('li', class_='section main clearfix')  # All topic sections

        for section in sections:
            section_resources = section.find_all('div', class_='activityinstance')
            for resource_div in section_resources:
                resource = Resource(resource_div)
                self.resources[resource.name] = resource
                if section == latest_week_section:
                    self.latest_resources.append(resource)

    def download_resource(self, req_name, destination_dir, update_handling):
        """
            Downloads the course resource with the requested name (req_name) to the path.
            The specified 'update_handling' is applied, if the file already exists.
            Currently supports files, folders and assignments.
        """
        try:
            print(f'Searching for resource {req_name} in course {self.name} ...')
            resource = self.resources.get(req_name, None)
            if resource is None:
                print(f'No resource matching {req_name} found')
            else:
                resource.download(destination_dir, update_handling)
        except:
            # TODO: add logging and log exception info (traceback to a file)
            print(f"Could not download any resource matching {req_name} due to an internal error.")

    def download_latest_resources(self, destination_dir, update_handling):
        print(f'Downloading latest resources for course {self.name} ...\n')
        if len(self.latest_resources) == 0:
            print('No resources categorized as "latest" found.')
        for resource in self.latest_resources:
            resource.download(destination_dir, update_handling)

    def list_all_resources(self):
        print(f'Listing all available resources for course {self.name} ...\n')
        for name, resource in self.resources.items():
            # TODO: check, check if resource is actually available for the user
            #  (see: https://github.com/NewLordVile/tum-moodle-downloader/issues/11)
            print(f"{name} ---- type: {resource.type}")

    def list_latest_resources(self):
        print('Listing latest resources ...\n')
        if len(self.latest_resources) == 0:
            print('No resources categorized as "latest" found.')
        for resource in self.latest_resources:
            print(f"{resource.name} ---- type: {resource.type}")

    def get_matching_resource_names(self, resource_pattern=".*"):
        resource_pattern = re.compile(resource_pattern)
        resource_names = []
        for name, resource in self.resources.items():
            if re.match(resource_pattern, resource.name):
                resource_names.append(resource.name)
        return resource_names

