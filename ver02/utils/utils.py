import os
import pickle
#STORAGE = './result/pkl/'
STORAGE = './result1031/pkl/'
#STORAGE = './new/'

def preserve(v, filename):
    with open(os.path.join(f'{STORAGE}',filename+".pkl"), 'wb') as f:
        pickle.dump(v,f)

def Load(filename):
    with open(os.path.join(f'{STORAGE}',filename),'rb') as f:
        v = pickle.load(f)
    return v
