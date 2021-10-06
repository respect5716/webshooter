import requests
from bs4 import BeautifulSoup

from .const import USER_AGENT

def url_to_soup(url):
    headers={'User-Agent': USER_AGENT}
    req = requests.get(url, headers=headers)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup