from authentication import start_session
from bs4 import BeautifulSoup
import os
from Course import Course


username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
semester = os.getenv('SEMESTER')


def list_courses():
    """
    Prints out all the courses of a given semester and returns a list containing the course names
    Semester to be specified in the format 'YEAR-TERM', e.g.
    '2019-2' for Winter Semester 2019/2020 or '2019-1' for Summer Semester 2019
    """
    courses = []
    driver, _ = start_session(username, password)
    select_term = driver.find_element_by_id('coc-filterterm')
    select_term.click()
    for term in select_term.find_elements_by_tag_name('option'):
        if term.get_attribute('value') == semester:
            term.click()
            break
    print('\nCourses for term: ' + semester + '\n')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    for div in soup.find_all('div', class_='termdiv coc-term-' + semester):
        title = div.find('h3').find('a').get('title')
        courses.append(title)
        print('\t' + title)
    return courses


def get_course(course_name):
    driver, session = start_session(username, password)
    select_term = driver.find_element_by_id('coc-filterterm')
    select_term.click()
    for term in select_term.find_elements_by_tag_name('option'):
        if term.get_attribute('value') == semester:
            term.click()
            break
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    for div in soup.find_all('div', class_='termdiv coc-term-' + semester):
        course = div.find('h3').find('a')
        if course_name in course.get('title'):
            return Course(course.get('href'), session)
