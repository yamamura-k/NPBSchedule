import os
import pickle
from functools import wraps
import time

STORAGE = './result/pkl/'
#STORAGE = './new/'

def preserve(v, filename):
    with open(os.path.join(f'{STORAGE}',filename+".pkl"), 'wb') as f:
        pickle.dump(v,f)

def Load(filename):
    with open(os.path.join(f'{STORAGE}',filename),'rb') as f:
        v = pickle.load(f)
    return v

def stop_watch(func):
    @wraps(func)
    def wrapper(*args, **kargs) :
        start = time.time()
        result = func(*args,**kargs)
        elapsed_time =  time.time() - start
        print(f"{func.__name__}は{elapsed_time}秒かかりました")
        return result
    return wrapper