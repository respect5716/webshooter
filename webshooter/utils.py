from dataclasses import dataclass
from typing import Optional, Callable, Union, List, Dict, Any, Type


def make_list(var):
    if type(var) != list:
        var = [var]
    return var
    
    
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
        
        
class Item(object):
    def __init__(self, data: Dict, key: str, parent: Optional[Type["Item"]]):
        self.data = data
        self.key = key
        self.parent = parent
    
    @property
    def val(self):
        return self.data[self.key]
    
    @property
    def attr(self):
        return {k:v for k,v in self.data.items() if k != self.key}
    
    
    def __repr__(self):
        return f"Item(key={self.key}, data={self.data})"