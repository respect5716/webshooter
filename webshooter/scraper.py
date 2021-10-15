import ray
import logging
import pandas as pd
from tqdm.auto import tqdm
from selenium import webdriver

from dataclasses import dataclass
from typing import Optional, Callable, List, Dict, Any

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
    
    
    def validation(self):
        required = ['browse', 'request', 'parse', 'merge', 'postprocess']
        for req in required:
            if req not in self.funcs.keys():
                raise Exception(f'function {req} is not registered')
        print('All functions are registered!')
    
    
    def browse(self):
        logging.info('Browsing started')
        fn = self.funcs['browse']
        self.urls = fn()
        logging.info('Browsing finished')
        
        
    def request(self):
        logging.info('Requesting started')
        fn = self.funcs['request']
        if fn.multiprocess:
            ray_fn = ray.remote(fn.fn)
            objs = [ray_fn.remote(url) for url in self.urls]
            objs = tqdm(objs, desc='request', display=self.progbar)
            for obj in objs:
                html = ray.get(obj)
                html = make_list(html)
                self.htmls += html
        
        else:
            urls = tqdm(self.urls, desc='request', display=self.progbar)
            for url in urls:
                html = fn(url)
                html = make_list(html)
                self.htmls += html
        logging.info('Requesting finished')
            
    
    def parse(self):
        logging.info('Parsing started')
        fn = self.funcs['parse']
        if fn.multiprocess:
            ray_fn = ray.remote(fn.fn)
            htmls = tqdm(self.htmls, desc='parse', display=self.progbar)
            for html in htmls:
                info = ray.get(ray_fn.remote(html))
                info = make_list(info)
                self.infos += info
#             objs = [ray_fn.remote(html) for html in self.htmls]
#             objs = tqdm(objs, desc='parse', display=self.progbar)
#             for obj in objs:
#                 info = ray.get(obj)
#                 info = make_list(info)
#                 self.infos += info
        
        else:
            htmls = tqdm(self.htmls, desc='parse', display=self.progbar)
            for html in htmls:
                info = fn(html)
                info = make_list(info)
                self.infos += info
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
        self.validation()
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