import time
import requests
from bs4 import BeautifulSoup

from const import HEADERS
from utils import error_message, return_exception


def static_request(
    url, 
    return_type = 'html', 
    headers = HEADERS, 
    proxies = [], 
    timeout = 5, 
    allow_redirects = True
):

    try:
        kwargs = {
            'headers': headers,
            'proxies': proxies,
            'timeout': timeout,
            'allow_redirects': allow_redirects
        }
        
        res = requests.get(url, **kwargs)
        if return_type == 'json':
            return res.json()
        elif return_type == 'html':
            return res.text
        else:
            return res
    
    except requests.exceptions.ReadTimeout:
        error_message('ReadTimeout', url)
        time.sleep(3)
        return return_exception(return_type)
        
    
    except Exception as e:
        error_message(e, url)
        return return_exception(return_type)


def dynamic_request(url, driver):
    driver.get(url)
    return driver.page_source


def url_to_soup(url):
    html = static_request(url)
    soup = BeautifulSoup(html)
    return soup