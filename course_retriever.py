from authentication import start_session
from bs4 import BeautifulSoup


def list_courses(semester='all'):
    driver = start_session()
    select_term = driver.find_element_by_id('coc-filterterm')
    select_term.click()
    for term in select_term.find_elements_by_tag_name('option'):
        if term.get_attribute('value') == semester:
            term.click()
            break
    print('Courses for term: ' + semester + '\n')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    for div in soup.find_all('div', class_='termdiv coc-term-' + semester):
        title = div.find('h3').find('a').get('title')
        print(title)
