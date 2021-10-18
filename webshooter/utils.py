from dataclasses import dataclass
from typing import Optional, Callable, Union, List, Dict, Any


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