import ray
import logging
import pandas as pd
from tqdm.auto import tqdm
from selenium import webdriver

from dataclasses import dataclass
from typing import Optional, Callable, Union, List, Dict, Any

from .request import static_request

def make_list(var):
    if type(var) != list:
        var = [var]
    return var

def default_merge(infos):
    return pd.DataFrame(infos)

def default_postprocess(table):
    return table
    
    
@dataclass
class Func:
    fn: Callable
    multiprocess: bool
        
    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)
        

class AttributeDict(Dict):
    def __getattr__(self, key: str) -> Optional[Any]:
        return self[key]
    
    def __setattr__(self, key: str, val: Any) -> None:
        self[key] = val
        
        
        
class Scraper(object):
    multiprocess_funcs = ['request', 'parse']
    
    def __init__(self, progbar: bool):
        self.progbar = progbar
        self.reset_funcs()
        self.reset_data()
        self.reset_vars()
        
        
    def reset_funcs(self):
        self.funcs = {}
        self.funcs['merge'] = Func(default_merge, False)
        self.funcs['postprocess'] = Func(default_postprocess, False)
    
    
    def reset_vars(self):
        self.v = AttributeDict()
    
    
    def reset_data(self):
        self.urls = []
        self.htmls = []
        self.infos = []
        self.table = None
        self.data = None
    
    def set_var(self, k, v):
        self.v[k] = v
        
    def set_vars(self, variables: Dict):
        for k, v in variables.items():
            self.v[k] = v
        

    def load_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
    
    
    @property
    def multiprocess(self):
        return any([self.funcs[f].multiprocess for f in self.multiprocess_funcs])
    
    
    def register(self, method: str, multiprocess: bool = False) -> Callable:
        if method not in self.multiprocess_funcs and multiprocess:
            logging.warning(f'func {method} is does not use multiprocessing')
        
        def decorator(f: Callable) -> Callable:
            self.funcs[method] = Func(f, multiprocess)
            return f
        return decorator
    
    
    def check_funcs(self):
        required = ['browse', 'request', 'parse', 'merge', 'postprocess']
        for req in required:
            if req not in self.funcs.keys():
                raise Exception(f'function {req} is not registered')
        logging.info('All functions are registered!')
    
    
    def check_res(self, res: Union[str, Dict, List[str], List[Dict]], required_key: str) -> List[Dict]:
        if type(res) == str:
            return [{required_key: res}]
        
        elif type(res) == dict:
            if required_key and required_key not in res:
                raise Exception(f'{required_key} is required!')
            return [res]
            
        elif type(res) == list:
            if type(res[0]) == str:
                return [{required_key: r} for r in res]
                
            elif type(res[0]) == dict:
                if required_key and required_key not in res[0]:
                    raise Exception(f'{required_key} is required!')
                return res
        
        raise Exception('result should be Union[str, Dict, List[str], List[Dict]]')

    
    def browse(self):
        logging.info('Browsing started')
        fn = self.funcs['browse']
        urls = fn()
        self.urls = self.check_res(urls, 'url')
        logging.info('Browsing finished')
        
        
    def request(self):
        logging.info('Requesting started')
        fn = self.funcs['request']
        
        htmls = []
        if fn.multiprocess:
            ray_fn = ray.remote(fn.fn)
            objs = [ray_fn.remote(url['url']) for url in self.urls]
            objs = tqdm(objs, desc='request') if self.progbar else objs
            for obj in objs:
                html = ray.get(obj)
                html = self.check_res(html, 'html')
                htmls += html
        
        else:
            urls = tqdm(self.urls, desc='request') if self.progbar else self.urls
            for url in urls:
                html = fn(url['url'])
                html = self.check_res(html, 'html')
                htmls += html
        
        self.htmls = htmls    
        logging.info('Requesting finished')
            
    
    def parse(self):
        logging.info('Parsing started')
        fn = self.funcs['parse']
        
        infos = []
        if fn.multiprocess:
            ray_fn = ray.remote(fn.fn)
            objs = [ray_fn.remote(html['html']) for html in self.htmls]
            objs = tqdm(objs, desc='parse') if self.progbar else objs
            for obj in objs:
                info = ray.get(obj)
                info = self.check_res(info, None)
                infos += info
        
        else:
            htmls = tqdm(self.htmls, desc='parse') if self.progbar else self.htmls
            for html in htmls:
                info = fn(html['html'])
                info = self.check_res(info, None)
                infos += info
                
        self.infos = infos
        logging.info('Parsing finished')
        
    
    def merge(self):
        logging.info('Merging started')
        self.table = self.funcs['merge'](self.infos)
        logging.info('Merging finished')
            
            
    def postprocess(self):
        logging.info('Postprocessing started')
        self.data = self.funcs['postprocess'](self.table)
        logging.info('Postprocessing finished')
    
    
    def run(self):
        self.check_funcs()
        if self.multiprocess:
            ray.init()
        
        self.browse()
        self.request()
        self.parse()
        self.merge()
        self.postprocess()
        
        if self.multiprocess:
            ray.shutdown()
        return self.data
    
    @classmethod
    def from_urls(cls, urls: List, progbar=True):
        app = cls(progbar=progbar)
        app.urls = urls
        
        @app.register('browse')
        def browse():
            return app.urls
        
        return app
        
        
class StaticScraper(Scraper):
    def __init__(self, progbar: bool):
        super().__init__(progbar)
        self.funcs['request'] = Func(static_request, False)
        
    @classmethod
    def from_urls(cls, urls: List, progbar=True):
        app = cls(progbar=progbar)
        app.urls = urls
        
        @app.register('browse')
        def browse():
            return app.urls
        
        return app    
        
        
class DynamicScraper(Scraper):
    def __init__(self, progbar: bool):
        super().__init__(progbar)
        self.load_webdriver()
        
        
    @classmethod
    def from_urls(cls, urls: List, progbar=True):
        app = cls(progbar=progbar)
        app.urls = urls
        
        @app.register('browse')
        def browse():
            return app.urls
        
        return app