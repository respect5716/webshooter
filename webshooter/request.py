import time
import logging
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
HEADERS = {'User-Agent': USER_AGENT}

def return_exception(return_type):
    if return_type == 'json':
        return {}
    elif return_type == 'html':
        return '<html></html>'
    else:
        return ''
        
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
        logging.error(f'ReadTimeout | {url}')
        time.sleep(3)
        return return_exception(return_type)
        
    
    except Exception as e:
        logging.error(f'{e} | {url}')
        return return_exception(return_type)
    
    
def url_to_soup(url):
    html = static_request(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup