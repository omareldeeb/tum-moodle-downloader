from bs4 import BeautifulSoup
from course import Course


def list_courses(session):
    response = session.get(
        'https://www.moodle.tum.de/my/',
        params={
            'coc-manage': '1',
        }
    )
    if response.status_code != 200:
        print(f'error in list_courses: {response.status_code}')

    soup = BeautifulSoup(response.text, 'html.parser')
    courses = soup.find_all('div', {'class': 'coursebox'})
    for course_div in courses:
        course = course_div.find('h3').find('a')

        title = course.get('title', None)
        print(title)


def get_course(session, course_name) -> Course or None:
    response = session.get(
        'https://www.moodle.tum.de/my/',
        params={
            'coc-manage': '1',
        }
    )

    if response.status_code != 200:
        print(f'error in get_course: {response.status_code}')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    courses = soup.find_all('div', {'class': 'coursebox'})

    for course_div in courses:
        course = course_div.find('h3').find('a')

        title = course.get('title', None)
        if not title:
            continue
        if course_name.lower() in title.lower():
            return Course(course.get('href'), session)
    print(f"Could not find course with name matching '{course_name}'")
    return None
