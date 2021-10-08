import requests
from selenium import webdriver

from const import HEADERS


def load_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

def error_message(error_type, url):
    print(f'ERROR | {error_type} | {url}')
    
def return_exception(return_type):
    if return_type == 'json':
        return {}
    elif return_type == 'html':
        return '<html></html>'
    else:
        return ''