import pandas as pd
from typing import Optional, Union, List, Dict

from .engine import StaticEngine, DynamicEngine


class Crawler(object):
    def __init__(self, 
        engine_type: str, 
        use_ray: bool, 
        use_tqdm: bool, 
        url_column: Optional[str] = None,
    ):  
        if engine_type not in ['static', 'dynamic']:
            raise Exception("engine type should be either 'static' or 'dynamic'")
    
        self.engine_type = engine_type
        self.use_ray = use_ray
        self.use_tqdm = use_tqdm
        self.url_column = url_column

        self.engine = StaticEngine() if engine_type == 'static' else DynamicEngine()


    def browse(self) -> List[str]:
        raise NotImplemented

    
    def parse(self, html) -> Union[List[Dict], Dict]:
        raise NotImplemented

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
        data = self.engine.run(urls, self.parse, self.use_ray, self.use_tqdm)
        data = self.merge(data, urls)
        data = self.postprocess(data)
        return data