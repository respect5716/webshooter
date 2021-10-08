import ray
import pandas as pd
from tqdm.auto import tqdm
from typing import Union, Optional, List, Dict

from utils import load_webdriver
from request import static_request, dynamic_request


class Crawler(object):
    def __init__(
        self,
        use_ray: bool,
        use_tqdm: bool = True,
        url_column: Optional[str] = None
    ):
        
        self.use_ray = use_ray
        self.use_tqdm = use_tqdm
        self.url_column = url_column
        
    
    def browse(self) -> List[str]:
        raise NotImplementedError

        
    def request(self, url: str) -> str:
        raise NotImplementedError
    
    
    def parse(self, html) -> Union[List[Dict], Dict]:
        raise NotImplementedError

        
    def merge(self, data, urls):
        if type(data[0]) == list:
            data = [pd.DataFrame(d) for d in data]
            if self.url_column:
                for d, u in zip(data, urls):
                    d[self.url_column] = u
            data = pd.concat(data, ignore_index=True)
        
        else:
            data = pd.DataFrame(data)      
            if self.url_column:
                data[self.url_column] = urls
        
        return data

    
    def postprocess(self, data):
        return data

    
    def crawl(self):
        urls = self.browse()
        
        htmls = []
        urls = tqdm(urls, desc='request') if self.use_tqdm else urls
        for url in urls:
            htmls.append(self.request(url))
            
        data = []
        if self.use_ray:
            ray.init()
            parse_fn = ray.remote(lambda x: self.parse(x))
            objs = [parse_fn.remote(html) for html in htmls]
            objs = tqdm(objs, desc='parse') if self.use_tqdm else objs
            for obj in objs:
                data.append(ray.get(obj))
            ray.shutdown()
        
        else:
            htmls = tqdm(htmls, desc='parse') if self.use_tqdm else htmls
            for html in htmls:
                data.append(self.parse(html))
            
        data = self.merge(data, urls)
        data = self.postprocess(data)
        return data
    
    
class StaticCrawler(Crawler):
    def request(self, url):
        return static_request(url)
    
    
class DynamicCrawler(Crawler):
    def __init__(self, use_ray, use_tqdm, url_column):
        super().__init__(use_ray, use_tqdm, url_column)
        self.driver = load_webdriver()
        
    def request(self, url):
        return dynamic_request(url, self.driver)