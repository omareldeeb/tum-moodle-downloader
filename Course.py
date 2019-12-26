from bs4 import BeautifulSoup
import requests
import os


class Course:
    def __init__(self, link, session):
        self.link = link
        self.session = session
        self.course_page = self.session.get(self.link).content
        self.soup = BeautifulSoup(self.course_page, 'html.parser').find('ul', class_='weeks')
        # self.weeks = self.get_weeks()

    def _download_file(self, url, path):
        print('Downloading file...')
        file = self.session.get(url)
        with open(path, 'wb') as f:
            f.write(file.content)
        print('\tDone.')

    def _download_folder(self, url):
        print('Downloading folder...')
        soup = BeautifulSoup(self.session.get(url).content, 'html.parser')
        dir_name = soup.find('div', role='main').find('h2').contents[0]
        print('\tCreating directory: ' + dir_name)
        os.mkdir(dir_name)
        files = soup.find_all('span', class_='fp-filename')
        for file in files:
            if len(file.contents) < 1:
                continue
            filename = file.contents[0]
            url = file.parent['href']
            self._download_file(url, dir_name + '/' + filename)

    def _download_assignment(self, url):
        print('Downloading assignment...')
        soup = BeautifulSoup(self.session.get(url).content, 'html.parser')
        file = soup.find('div', class_='fileuploadsubmission').find('a')
        filename = file.contents[0]
        url = file['href']
        self._download_file(url, filename)

    def download_resource(self, name):
        print('Searching for resource: ' + name)
        sections = self.soup.find_all('li', class_='section main clearfix')
        sections.append(self.soup.find('li', class_='section main clearfix current'))
        for section in sections:
            resources = section.find_all('div', class_='activityinstance')
            for resource in resources:
                found_name = resource.find('span', class_='instancename').contents[0]
                if name in found_name:
                    group = resource.parent.parent.parent.parent['class']
                    if group == ['activity', 'resource', 'modtype_resource']:
                        print('\tFound file: ' + found_name)
                        self._download_file(resource.find('a')['href'], found_name)
                    elif group == ['activity', 'folder', 'modtype_folder']:
                        print('\tFound folder: ' + found_name)
                        self._download_folder(resource.find('a')['href'])
                    elif group == ['activity', 'assign', 'modtype_assign']:
                        print('\tFound assignment: ' + found_name)
                        self._download_assignment(resource.find('a')['href'])

    def download_latest_resources(self):
        latest_section = self.soup.find('li', class_='section main clearfix current')
        latest_resources = latest_section.find_all('div', class_='activityinstance')
        for resource in latest_resources:
            resource_name = resource.find('span', class_='instancename').contents[0]
            self.download_resource(resource_name)
