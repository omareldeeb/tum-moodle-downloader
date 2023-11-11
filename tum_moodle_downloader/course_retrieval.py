from bs4 import BeautifulSoup

from .course import Course
import tum_moodle_downloader.globals as globals


def list_courses():
    print('Listing available courses: ')
    for course_div in _get_course_divs():
        course = course_div.find('h3').find('a')

        title = course.get('title', None)
        print(f'\u001B[36m{title}\u001B[0m')


def get_course(course_name) -> Course or None:
    for course_div in _get_course_divs():
        course = course_div.find('h3').find('a')

        title = course.get('title', None)
        if not title:
            continue
        # TODO: consider using regex for finding a matching course
        # TODO: handle multiple matching courses
        if course_name.lower() in title.lower():
            return Course(title, course.get('href'))
    print(f"Could not find course with name matching \u001B[31m{course_name}\u001B[0m")
    return None


def _get_course_divs():
    response = globals.global_session.get(
        'https://www.moodle.tum.de/my/',
        params={
            'coc-manage': '1',
        }
    )
    if response.status_code != 200:
        print(f'error while retrieving course page: status_code={response.status_code}')
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    course_divs = soup.find_all('div', {'class': 'coursebox'})

    return course_divs
