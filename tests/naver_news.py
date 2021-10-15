from context import webshooter
from webshooter import StaticScraper, url_to_soup
from bs4 import BeautifulSoup

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

app = StaticScraper(progbar = True)
app.set_vars(config)

def get_page_url(category, date, page):
    category_id = app.v.category_to_id[category]
    url = f'https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={category_id}&listType=title&date={date}&page={page}'
    return url

def find_max_page(category):
    page_url = get_page_url(category, app.v.date, 10000)
    soup = url_to_soup(page_url)
    max_page = soup.select('div.paging strong')[0].text
    return min(app.v.max_page, int(max_page))

@app.register('browse')
def browse():
    urls = []
    for category in app.v.categories:
        max_page = find_max_page(category)
        urls += [get_page_url(category, app.v.date, p) for p in range(1, max_page+1)]
    return urls

@app.register('parse', multiprocess=False)
def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select('div.list_body ul.type02 a')
    titles = [i.text for i in articles]
    urls = [i.get('href') for i in articles]
    authors = [i.text for i in soup.select('div.list_body ul.type02 span.writing')]
    return [{'title': t, 'author': a, 'url':u} for t, a, u in zip(titles, authors, urls)]
    
    

if __name__ == '__main__':
    data = app.run()
    data.to_csv('naver_news.csv', index=False)