from bs4 import BeautifulSoup
import requests
import os


class Course:
    def __init__(self, link, session):
        self.link = link
        self.session = session
        # self.weeks = self.get_weeks()

    def get_weeks(self):
        print('getting resources...')
        course_page = self.session.get(self.link).content
        weeks = []
        soup = BeautifulSoup(course_page, 'html.parser').find('ul', class_='weeks')
        for child in soup.contents:
            resources = child.find_all('li')
            for resource in resources:
                if resource['class'] == ['activity', 'resource', 'modtype_resource']:
                    url = resource.find('a')['href']
                    print('Downloading file...')
                    file = self.session.get(url)
                    with open(os.path.basename(file.url), 'wb') as f:
                        f.write(file.content)
                    break
            break

        return weeks