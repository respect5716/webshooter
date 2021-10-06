import time
import ray
import requests
import pandas as pd
from tqdm.auto import tqdm
from typing import Callable, Optional, Union, List, Dict

from .const import USER_AGENT, FALLBACK_RESPONSE




class StaticEngine(object):
    def __init__(self,
        user_agent: str = USER_AGENT, 
        proxies: Dict = {}, 
        timeout: Union[int, float] = 5
    ):
        self.user_agent = user_agent
        self.proxies = proxies
        self.timeout = timeout
    
    @property
    def request_kwargs(self) -> Dict:
        return {
            'headers': {'User-Agent': self.user_agent},
            'proxies': self.proxies,
            'timeout': self.timeout,
            'allow_redirects': True,
        }
    
    def error_message(self, error_type, url):
        print(f'ERROR | {error_type} | {url}')
    
    def request(self, url: str) -> str:
        try:
            res = requests.get(url, **self.request_kwargs)
        
        except requests.exceptions.ReadTimeout:
            self.error_message('ReadTimeout', url)
            time.sleep(10)
            return FALLBACK_RESPONSE
        
        except Exception as e:
            self.error_message(e, url)
            return FALLBACK_RESPONSE
        
        return res.text
    

    def run(self, 
        urls: List[str], 
        parse_fn: Callable[[str], Union[List[Dict], Dict]], 
        use_ray: bool,
        use_tqdm: bool = True,
        ) -> pd.DataFrame:
        
        htmls = []
        urls = tqdm(urls, desc='request') if use_tqdm else urls
        for url in urls:
            htmls.append(self.request(url))
        
        data = []
        
        if use_ray:
            ray.init()
            parse_fn = ray.remote(parse_fn)
            objs = [parse_fn.remote(html) for html in htmls]
            objs = tqdm(objs, desc='parse') if use_tqdm else objs
            for obj in objs:
                data.append(ray.get(obj))            
            ray.shutdown()
            
        else:
            htmls = tqdm(htmls, desc='parse') if use_tqdm else htmls
            for html in htmls:
                data.append(parse_fn(html))

        return data


class DynamicEngine(object):
    def crawl(self):
        return