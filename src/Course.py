from bs4 import BeautifulSoup
import os


class Course:
    def __init__(self, link, session):
        self.link = link
        self.session = session
        self.course_page = self.session.get(self.link).content
        self.soup = BeautifulSoup(self.course_page, 'html.parser').find('ul', class_='weeks')
        self.sections = self.soup.find_all('li', class_='section main clearfix')  # All sections
        self.sections.append(self.soup.find('li', class_='section main clearfix current'))  # Latest section

    def _download_file(self, url, path):
        print('Downloading file...')
        file = self.session.get(url)
        filename = os.path.basename(file.url)
        if '?forcedownload=1' in filename:
            filename = filename.replace('?forcedownload=1', '')  # Removes 'forcedownload=1' parameter from the url
        path = os.path.join(path, filename)
        with open(path, 'wb') as f:
            f.write(file.content)
        print('Done. Saved to: ' + path)

    def _download_folder(self, url, path):
        print('Downloading folder...')
        soup = BeautifulSoup(self.session.get(url).content, 'html.parser')  # Get folder page
        dir_name = soup.find('div', role='main').find('h2').contents[0]  # Find folder title
        print('Creating directory: ' + dir_name)  # Create the directory
        os.mkdir(os.path.join(path, dir_name))
        files = soup.find_all('span', class_='fp-filename')  # Finds all files in folder page
        for file in files:
            if len(file.contents) < 1:
                continue
            filename = file.contents[0]
            url = file.parent['href']
            self._download_file(url, os.path.join(path, dir_name))

    def _download_assignment(self, url, path):
        print('Extracting file from assignment...')
        soup = BeautifulSoup(self.session.get(url).content, 'html.parser')
        file = soup.find('div', class_='fileuploadsubmission').find('a')
        if len(file.contents) < 1:
            print('No file found')
            return
        url = file['href']
        self._download_file(url, path)

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

    def download_resource(self, name, path):
        """
        Downloads all course resources matching the given name to the given path.
        Currently supports files, folders and assignments.
        """
        if not os.path.exists(path):
            print(path + ' not found. Creating path: ' + path)
            try:
                os.mkdir(path)
            except FileNotFoundError:
                print('Could not create path. Please check the given path and try again.')
                exit()
        found = False
        print('Searching for resource: ' + name)
        for section in self.sections:
            resources = section.find_all('div', class_='activityinstance')
            for resource in resources:
                found_name = resource.find('span', class_='instancename').contents[0]
                if name in found_name:
                    resource_type = self._get_resource_type(resource)
                    if resource_type == 'file':
                        print('Found file: ' + found_name)
                        found = True
                        self._download_file(resource.find('a')['href'], path)
                    elif resource_type == 'folder':
                        print('Found folder: ' + found_name)
                        found = True
                        self._download_folder(resource.find('a')['href'], path)
                    elif resource_type == 'assignment':
                        print('Found assignment: ' + found_name)
                        found = True
                        self._download_assignment(resource.find('a')['href'], path)
        if not found:
            print('No resources found matching ' + name)

    def download_latest_resources(self):
        latest_section = self.soup.find('li', class_='section main clearfix current')
        latest_resources = latest_section.find_all('div', class_='activityinstance')
        if len(latest_resources) == 0:
            print('No new resources found')
        for resource in latest_resources:
            resource_name = resource.find('span', class_='instancename').contents[0]
            self.download_resource(resource_name)

    def list_all_resources(self):
        print('Listing all course resources:\n')
        for section in self.sections:
            resources = section.find_all('div', class_='activityinstance')
            for resource in resources:
                resource_type = self._get_resource_type(resource)
                print(resource.find('span', class_='instancename').contents[0] + ' ---- type: ' + resource_type)

    def list_recent_resources(self):
        print('Listing recent resources:\n')
        latest_section = self.soup.find('li', class_='section main clearfix current')
        latest_resources = latest_section.find_all('div', class_='activityinstance')
        if len(latest_resources) == 0:
            print('No new resources found')
        for resource in latest_resources:
            resource_type = self._get_resource_type(resource)
            print(resource.find('span', class_='instancename').contents[0] + ' ---- type: ' + resource_type)
