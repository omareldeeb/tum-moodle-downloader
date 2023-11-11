import asyncio
import os
import urllib
from dateutil.parser import parse as parsedate
import datetime
from enum import Enum

from bs4 import BeautifulSoup

import tum_moodle_downloader.globals as globals


def background(f):
    def wrapped(*args):
        return asyncio.get_event_loop().run_in_executor(None, f, *args)

    return wrapped


class ResourceType(Enum):
    RESOURCE_TYPE_FILE = "file"
    RESOURCE_TYPE_FOLDER = "folder"
    RESOURCE_TYPE_ASSIGNMENT = "assignment"
    RESOURCE_TYPE_URL = "url"
    RESOURCE_TYPE_OTHER = "other"

    def __repr__(self):
        if self == ResourceType.RESOURCE_TYPE_FILE:
            return "File 📄"
        if self == ResourceType.RESOURCE_TYPE_FOLDER:
            return "Folder 📂"
        if self == ResourceType.RESOURCE_TYPE_ASSIGNMENT:
            return "Assignment 📝"
        if self == ResourceType.RESOURCE_TYPE_URL:
            return "Link 🔗"
        if self == ResourceType.RESOURCE_TYPE_OTHER:
            return "Other"

        return "Unknown ❔"


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
        if 'modtype_resource' in group:
            return ResourceType.RESOURCE_TYPE_FILE
        elif 'modtype_folder' in group:
            return ResourceType.RESOURCE_TYPE_FOLDER
        elif 'modtype_assign' in group:
            return ResourceType.RESOURCE_TYPE_ASSIGNMENT
        elif 'modtype_url' in group:
            # TODO what to do with other types?
            if 'pdf' in resource_div.find('img')['src']:
                return ResourceType.RESOURCE_TYPE_URL
        return ResourceType.RESOURCE_TYPE_OTHER

    @staticmethod
    def _download_file(url, destination_dir, update_handling):
        # Extract header information of the file before actually downloading it
        # Redirects MUST be enabled otherwise this won't work for files which are to be downloaded directly from the
        # course's home page (--> example: redirect from https://www.moodle.tum.de/mod/resource/view.php?id=831037
        # to https://www.moodle.tum.de/pluginfile.php/1702929/mod_resource/content/1/%C3%9Cbung%202_L%C3%B6sung.pdf)
        file_head = globals.global_session.head(url, allow_redirects=True)

        # Use 'file_head.headers' to access the files headers. Interesting headers include:
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
                print(f"Skipping file \u001B[35m{filename}\u001B[0m because it already exists at {destination_path}")
                return
            if update_handling == "add":
                # Create filename "filename (i).extension" and add it as a new version of the file
                i = 1
                (root, ext) = os.path.splitext(filename)
                while file_exists:
                    destination_path = os.path.join(destination_dir, root + ' (' + str(i) + ')' + ext)
                    i += 1
                    file_exists = os.path.exists(destination_path)
            if update_handling == "update":
                url_time = file_head.headers['last-modified']
                url_date = parsedate(url_time).astimezone()
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(destination_path)).astimezone()
                if url_date <= file_time:
                    print(f"Skipping file \u001B[35m{filename}\u001B[0m because it is already the latest version")
                    return

        print(f'Downloading file \u001B[35m{filename}\u001B[0m')
        file = globals.global_session.get(url)
        print('Done downloading.')

        print(f'Saving file \u001B[35m{filename}\u001B[0m')
        with open(destination_path, 'wb') as f:
            f.write(file.content)
        print('Done. Saved to: ' + destination_path)

    @staticmethod
    def _download_folder(file_url, destination_path, update_handling):
        print('Downloading folder')
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
        print('Extracting files from assignment')
        # Get assignment page
        assignment_soup = BeautifulSoup(globals.global_session.get(file_url).content, 'html.parser')
        file_anchors = assignment_soup.find('div', id='intro').find_all('div', class_='fileuploadsubmission')
        if len(file_anchors) == 0:
            print('No file found')
            return
        for file_anchor in file_anchors:
            file_url = file_anchor.find('a')['href']
            Resource._download_file(file_url, destination_path, update_handling)

    @background
    def download_parallel(self, destination_dir, update_handling):
        self.download(destination_dir, update_handling)

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
        print(f"Attempting to download resource \u001B[35m{self.name}\u001B[0m with type \u001B[34;1m{self.type.__repr__()}" +
              "\u001B[0m")
        if self.type == ResourceType.RESOURCE_TYPE_FILE or self.type == ResourceType.RESOURCE_TYPE_URL:
            Resource._download_file(self.resource_url, destination_dir, update_handling)
        elif self.type == ResourceType.RESOURCE_TYPE_FOLDER:
            Resource._download_folder(self.resource_url, destination_dir, update_handling)
        elif self.type == ResourceType.RESOURCE_TYPE_ASSIGNMENT:
            Resource._download_assignment(self.resource_url, destination_dir, update_handling)
        else:
            print(f"Cannot download resource \u001B[35m{self.name}\u001B[0m of type \u001B[34;1m{self.type}\u001B[0m" +
                  f" is not supported!")
