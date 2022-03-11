import os
import urllib

from bs4 import BeautifulSoup

import globals


class Resource:
    def __init__(self, resource_div, is_recent):
        self.resource_div = resource_div
        self.is_recent = is_recent
        self.name = Resource.get_resource_name(self.resource_div)
        self.resource_url = Resource.get_resource_url(self.resource_div)
        if self.resource_url is None:
            self.available = False
        else:
            # TODO: validate url to check, if it is available
            self.available = True
        self.type = self.get_resource_type(self.resource_div)

    @staticmethod
    def get_resource_name(resource_div):
        return resource_div.find('span', class_='instancename').contents[0].strip()

    @staticmethod
    def get_resource_url(resource_div):
        resource_url_anchor = resource_div.find('a')
        if resource_url_anchor is None:
            return None
        else:
            return resource_url_anchor.get('href', None)

    @staticmethod
    def get_resource_type(resource_div):
        group = resource_div.parent.parent.parent.parent['class']
        if group == ['activity', 'resource', 'modtype_resource']:
            return 'file'
        elif group == ['activity', 'folder', 'modtype_folder']:
            return 'folder'
        elif group == ['activity', 'assign', 'modtype_assign']:
            return 'assignment'
        elif group == ['activity', 'url', 'modtype_url']:
            # TODO what to do with other types?
            if 'pdf' in resource_div.find('img')['src']:
                return 'url'
        return 'other (e.g. quiz, forum, ...)'

    @staticmethod
    def _download_file(url, destination_dir, update_handling):
        # Extract header information of the file before actually downloading it
        # Redirects MUST be enabled otherwise this won't work for files which are to be downloaded directly from the
        # course's home page (--> example: redirect from https://www.moodle.tum.de/mod/resource/view.php?id=831037
        # to https://www.moodle.tum.de/pluginfile.php/1702929/mod_resource/content/1/%C3%9Cbung%202_L%C3%B6sung.pdf)
        file_head = globals.global_session.head(url, allow_redirects=True)

        # Use 'file_head.headers' to access the files headers. Interesting headers include:
        # - 'Last-Modified' (Date and time when the file on Moodle was modified the last time)
        # --> TODO: only replace local file, if the file on Moodle is newer than the local one
        # - 'Content-Length'
        # --> TODO: consider asking for the user's consent before downloading a huge file
        # - 'Content-Type'

        file_url = file_head.url
        # Decode encoded URL (for more info see: https://www.urldecoder.io/python/) to get rid of "percent encoding"
        # (as in https://www.moodle.tum.de/pluginfile.php/1702929/mod_resource/content/1/%C3%9Cbung%202_L%C3%B6sung.pdf)
        decoded_file_url = urllib.parse.unquote(file_url)

        # Extract file name from URL
        filename = os.path.basename(decoded_file_url)
        if '?forcedownload=1' in filename:
            filename = filename.replace('?forcedownload=1', '')

        destination_path = os.path.join(destination_dir, filename)

        # Apply update handling in case the file already exists
        file_exists = os.path.exists(destination_path)
        if file_exists and update_handling != "replace":
            if update_handling == "skip":
                print(f"Skipping file {filename} because it already exists at {destination_path}")
                return
            if update_handling == "add":
                # Create filename "filename (i).extension" and add it as a new version of the file
                i = 1
                (root, ext) = os.path.splitext(filename)
                while file_exists:
                    destination_path = os.path.join(destination_dir, root + ' (' + str(i) + ')' + ext)
                    i += 1
                    file_exists = os.path.exists(destination_path)

        print(f'Downloading file {filename} ...')
        file = globals.global_session.get(url)
        print('Done downloading.')

        print(f'Saving file {filename} ...')
        with open(destination_path, 'wb') as f:
            f.write(file.content)
        print('Done. Saved to: ' + destination_path)

    @staticmethod
    def _download_folder(file_url, destination_path, update_handling):
        print('Downloading folder...')
        folder_soup = BeautifulSoup(globals.global_session.get(file_url).content, 'html.parser')  # Get folder page
        dir_name = folder_soup.find('div', role='main').find('h2').contents[0]  # Find folder title
        folder_path = os.path.join(destination_path, dir_name)
        if not os.path.exists(folder_path):
            print(f'Creating directory: {dir_name} in {destination_path}')
            os.mkdir(folder_path)
        files = folder_soup.find_all('span', class_='fp-filename')  # Finds all files in folder page
        for file in files:
            if len(file.contents) < 1:
                continue
            file_url = file.parent['href']
            Resource._download_file(file_url, folder_path, update_handling)

    @staticmethod
    def _download_assignment(file_url, destination_path, update_handling):
        print('Extracting files from assignment...')
        # Get assignment page
        assignment_soup = BeautifulSoup(globals.global_session.get(file_url).content, 'html.parser')
        file_anchors = assignment_soup.find('div', id='intro').find_all('div', class_='fileuploadsubmission')
        if len(file_anchors) == 0:
            print('No file found')
            return
        for file_anchor in file_anchors:
            file_url = file_anchor.find('a')['href']
            Resource._download_file(file_url, destination_path, update_handling)

    def download(self, destination_dir, update_handling):
        if not os.path.exists(destination_dir):
            print(destination_dir + ' not found. Creating path: ' + destination_dir)
            try:
                # Create path (recursively)
                os.makedirs(destination_dir)
            except FileNotFoundError:
                print(f'Could not create path {destination_dir}. Please check the path and try again.')
                return
        # TODO: check, check if resource is actually available for the user
        #  (see: https://github.com/NewLordVile/tum-moodle-downloader/issues/11)
        print(f"Attempting to download resource {self.name} with type {self.type} ...")
        if self.type == 'file' or self.type == 'url':
            Resource._download_file(self.resource_url, destination_dir, update_handling)
        elif self.type == 'folder':
            Resource._download_folder(self.resource_url, destination_dir, update_handling)
        elif self.type == 'assignment':
            Resource._download_assignment(self.resource_url, destination_dir, update_handling)
        else:
            print(f"Cannot download resource '{self.name}': type '{self.type}' is not supported!")
