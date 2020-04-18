import os
import re
import urllib.parse

from bs4 import BeautifulSoup


class Course:
    def __init__(self, link, session):
        self.link = link
        self.session = session
        self.course_page = self.session.get(self.link).content
        self.soup = BeautifulSoup(self.course_page, 'html.parser').find('ul', class_='weeks')
        self.sections = self.soup.find_all('li', class_='section main clearfix')  # All sections
        self.sections += (self.soup.find_all('li', class_='section main clearfix current'))  # Latest section

    def _download_file(self, url, destination_dir, update_handling):
        print('Downloading file...')
        file = self.session.get(url)

        # Decode encoded URL (for more info see: https://www.urldecoder.io/python/)
        decoded_file_url = urllib.parse.unquote(file.url)
        filename = os.path.basename(decoded_file_url)
        if '?forcedownload=1' in filename:
            filename = filename.replace('?forcedownload=1', '')  # Removes 'forcedownload=1' parameter from the url

        destination_path = os.path.join(destination_dir, filename)

        file_exists = os.path.exists(destination_path)
        if file_exists and update_handling != "replace":
            if update_handling == "skip":
                print(f"Skipping file {destination_path} because it already exists.")
                return
            if update_handling == "add":
                # Create filename "file (n)" and add it as a new version of the file
                i = 1
                # TODO How to get the most current one?
                (root, ext) = os.path.splitext(filename)
                while file_exists:
                    destination_path = os.path.join(destination_dir, root + ' (' + str(i) + ')' + ext)
                    i += 1
                    file_exists = os.path.exists(destination_path)

        with open(destination_path, 'wb') as f:
            f.write(file.content)
        print('Done. Saved to: ' + destination_path)

    def _download_folder(self, url, destination_path, update_handling):
        print('Downloading folder...')
        soup = BeautifulSoup(self.session.get(url).content, 'html.parser')  # Get folder page
        dir_name = soup.find('div', role='main').find('h2').contents[0]  # Find folder title
        path = os.path.join(destination_path, dir_name)
        if not os.path.exist(path):
            print('Creating directory: ' + dir_name)  # Create the directory
            os.mkdir(path)
        files = soup.find_all('span', class_='fp-filename')  # Finds all files in folder page
        for file in files:
            if len(file.contents) < 1:
                continue
            url = file.parent['href']
            self._download_file(url, path, update_handling)

    def _download_assignment(self, url, destination_path, update_handling):
        print('Extracting file from assignment...')
        soup = BeautifulSoup(self.session.get(url).content, 'html.parser')
        file = soup.find('div', class_='fileuploadsubmission').find('a')
        if len(file.contents) < 1:
            print('No file found')
            return
        url = file['href']
        self._download_file(url, destination_path, update_handling)

    @staticmethod
    def _get_resource_type(resource):
        group = resource.parent.parent.parent.parent['class']
        if group == ['activity', 'resource', 'modtype_resource', '']:  # Found resource is a file
            return 'file'
        elif group == ['activity', 'folder', 'modtype_folder', '']:  # Found resource is a folder
            return 'folder'
        elif group == ['activity', 'assign', 'modtype_assign', '']:  # Found resource is an assignment
            return 'assignment'
        return 'other (e.g. quiz, forum, ...)'

    def download_resource(self, req_name, path, update_handling):
        """
        Downloads all course resources matching the given name to the given path.
        Currently supports files, folders and assignments.
        """
        if not os.path.exists(path):
            print(path + ' not found. Creating path: ' + path)
            try:
                os.makedirs(path)
            except FileNotFoundError:
                print('Could not create path. Please check the given path and try again.')
                exit()
        found = False
        print('Searching for resource: ' + req_name)
        for section in self.sections:
            resources = section.find_all('div', class_='activityinstance')
            for resource in resources:
                found_name = resource.find('span', class_='instancename').contents[0].strip()
                if req_name == found_name:
                    resource_type = self._get_resource_type(resource)
                    if resource_type == 'file':
                        print('Found file: ' + found_name)
                        found = True
                        self._download_file(resource.find('a')['href'], path, update_handling)
                    elif resource_type == 'folder':
                        print('Found folder: ' + found_name)
                        found = True
                        self._download_folder(resource.find('a')['href'], path, update_handling)
                    elif resource_type == 'assignment':
                        print('Found assignment: ' + found_name)
                        found = True
                        self._download_assignment(resource.find('a')['href'], path, update_handling)
        if not found:
            print('No resources found matching ' + req_name)

    def download_latest_resources(self):
        latest_section = self.soup.find('li', class_='section main clearfix current')
        latest_resources = latest_section.find_all('div', class_='activityinstance')
        if len(latest_resources) == 0:
            print('No new resources found')
        for resource in latest_resources:
            resource_name = resource.find('span', class_='instancename').contents[0].strip()
            self.download_resource(resource_name)

    def list_all_resources(self):
        print('Listing all available resources:\n')
        for section in self.sections:
            resources = section.find_all('div', class_='activityinstance')
            for resource in resources:
                resource_type = self._get_resource_type(resource)
                if resource_type == 'file' or resource_type == 'folder' or resource_type == 'assignment':
                    print(resource.find('span', class_='instancename').contents[
                              0].strip() + ' ---- type: ' + resource_type)

    def list_recent_resources(self):
        print('Listing recent resources:\n')
        latest_section = self.soup.find('li', class_='section main clearfix current')
        latest_resources = latest_section.find_all('div', class_='activityinstance')
        if len(latest_resources) == 0:
            print('No new resources found')
        for resource in latest_resources:
            resource_type = self._get_resource_type(resource)
            print(resource.find('span', class_='instancename').contents[0] + ' ---- type: ' + resource_type)

    def get_matching_resource_names(self, resource_pattern=".*"):
        resource_pattern = re.compile(resource_pattern)
        resource_names = []
        for section in self.sections:
            resources = section.find_all('div', class_='activityinstance')
            for resource in resources:
                resource_type = self._get_resource_type(resource)
                if resource_type == 'file' or resource_type == 'folder' or resource_type == 'assignment':
                    resource_name = resource.find('span', class_='instancename').contents[0].strip()
                    if re.match(resource_pattern, resource_name):
                        resource_names.append(resource_name)
        return resource_names


