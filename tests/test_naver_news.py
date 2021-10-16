import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from bs4 import BeautifulSoup
from newspaper import Article

from webshooter import StaticScraper, url_to_soup


import logging
logging.root.setLevel(logging.INFO)

config = {
    'date': '20211012',
    'max_page': 1,
    'categories': ['정치', '경제', '사회', '세계', '생활/문화', 'IT/과학'],
    'category_to_id': {
        '정치': '100',
        '경제': '101',
        '사회': '102',
        '생활/문화': '103',
        '세계': '104',
        'IT/과학': '105',
    }
}

list_app = StaticScraper(progbar = True)
list_app.set_vars(config)
article_app = StaticScraper(progbar = True)

def get_page_url(category, date, page):
    category_id = list_app.v.category_to_id[category]
    url = f'https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={category_id}&listType=title&date={date}&page={page}'
    return url

def find_max_page(category):
    page_url = get_page_url(category, list_app.v.date, 10000)
    soup = url_to_soup(page_url)
    max_page = soup.select('div.paging strong')[0].text
    return min(list_app.v.max_page, int(max_page))

@list_app.register('browse')
def browse():
    urls = []
    for category in list_app.v.categories:
        max_page = find_max_page(category)
        urls += [get_page_url(category, list_app.v.date, p) for p in range(1, max_page+1)]
    return urls

@list_app.register('parse', multiprocess=True)
def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select('div.list_body ul.type02 a')
    titles = [i.text for i in articles]
    urls = [i.get('href') for i in articles]
    authors = [i.text for i in soup.select('div.list_body ul.type02 span.writing')]
    return [{'title': t, 'author': a, 'url':u} for t, a, u in zip(titles, authors, urls)]

@article_app.register('browse')
def browse_article():
    return article_app.v.meta['url'].to_list()
    
@article_app.register('parse', multiprocess=True)
def parse_article(html):
    article = Article('', language='ko', fetch_images=False)
    article.download(html)
    article.parse()
    text = article.text
    return {'text': text}
    

@article_app.register('postprocess')
def postprocess(table):
    data = pd.concat([article_app.v.meta, table], axis=1)
    return data

def test_naver_news():
    meta = list_app.run()
    meta = meta.sample(100).reset_index(drop=True)
    article_app.set_var('meta', meta)
    
    data = article_app.run()
    data.to_csv('naver_news.csv', index=False)
    print(data.head())

test_naver_news()