from bs4 import BeautifulSoup
from Course import Course


# def list_courses():
#     """
#     Prints out all the courses of a given semester and returns a list containing the course names
#     Semester to be specified in the format 'YEAR-TERM', e.g.
#     '2019-2' for Winter Semester 2019/2020 or '2019-1' for Summer Semester 2019
#     """
#     courses = []
#     driver, _ = start_session(username, password)
#     select_term = driver.find_element_by_id('coc-filterterm')
#     select_term.click()
#     for term in select_term.find_elements_by_tag_name('option'):
#         if term.get_attribute('value') == semester:
#             term.click()
#             break
#     print('\nCourses for term: ' + semester + '\n')
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     for div in soup.find_all('div', class_='termdiv coc-term-' + semester):
#         title = div.find('h3').find('a').get('title')
#         courses.append(title)
#         print('\t' + title)
#     return courses


def get_course(session, course_name) -> Course or None:
    # select_term = driver.find_element_by_id('coc-filterterm')
    # select_term.click()
    # for term in select_term.find_elements_by_tag_name('option'):
    #     if term.get_attribute('value') == semester:
    #         term.click()
    #         break

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

    # print(soup)
    courses = soup.find_all('div', {'class': 'coursebox'})
    # print(courses)

    for course_div in courses:
        course = course_div.find('h3').find('a')

        title = course.get('title', None)
        if not title:
            # todo: better error handling
            print(course)
            return None

        if course_name.lower() in title.lower():
            return Course(course.get('href'), session)
