import json
import re

from bs4 import BeautifulSoup

import globals
from resource import Resource


class Course:
    def __init__(self, course_name, course_url):
        self.name = course_name

        course_page = globals.global_session.get(course_url).content
        self.soup = BeautifulSoup(course_page, 'html.parser')

        self.resources = self._extract_resources()
        self.latest_resources = [resource for resource in self.resources.values() if resource.is_recent]

    def _extract_resources(self):
        resources = {}
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

        # Extract resources from the sections
        for section in sections:
            section_resources = section.find_all('div', class_='activityinstance')
            for resource_div in section_resources:
                resource = Resource(resource_div, is_recent=(section == latest_week_section))
                resources[resource.name] = resource

        return resources

    def download_resource(self, resource_name, destination_dir, update_handling):
        """
            Downloads the course resource with the requested name 'resource_name' to the path 'destination_dir'.
            The specified 'update_handling' is applied, if the file already exists.
            Currently supports files, folders and assignments.
        """
        try:
            print(f'Searching for resource {resource_name} in course {self.name} ...')
            resource = self.resources.get(resource_name, None)
            if resource is None:
                print(f'No resource matching {resource_name} found')
            else:
                with open(globals.DOWNLOAD_CONFIG_PATH, mode='r', encoding='utf-8') as json_file:
                    config_data = json.load(json_file)[0]
                if config_data['parallel_downloads']:
                    resource.download_parallel(destination_dir, update_handling)
                else:
                    resource.download(destination_dir, update_handling)
        except:
            # TODO: add logging and log exception info (traceback to a file)
            print(f"Could not download any resource matching {resource_name} due to an internal error.")

    def download_latest_resources(self, destination_dir, update_handling):
        print(f'Downloading latest resources for course {self.name} ...\n')
        if len(self.latest_resources) == 0:
            print('No resources categorized as "latest" found.')
        with open(globals.DOWNLOAD_CONFIG_PATH, mode='r', encoding='utf-8') as json_file:
            config_data = json.load(json_file)
            parallel = config_data.get('course_name', bool)
        for resource in self.latest_resources:
            if parallel:
                resource.download_parallel(destination_dir, update_handling)
            else:
                resource.download(destination_dir, update_handling)

    def list_all_resources(self):
        print(f'Listing all available resources for course {self.name} ...\n')
        for name, resource in self.resources.items():
            # TODO: check, check if resource is actually available for the user
            #  (see: https://github.com/NewLordVile/tum-moodle-downloader/issues/11)
            print(f"{name} ---- type: {resource.type}")

    def list_all_files(self):
        print(f'Listing all available resources for course {self.name} ...\n')
        for name, resource in self.resources.items():
            if resource.type == "file":
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
