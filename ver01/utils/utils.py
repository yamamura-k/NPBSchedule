import os
import pickle

def preserve(h, v, filename):
    with open(os.path.join('./result/',filename+"_h.pkl"), 'wb') as f:
        pickle.dump(h,f)
    with open(os.path.join('./result/',filename+"_v.pkl"), 'wb') as f:
        pickle.dump(v,f)

def Load(filename_h,filename_v):
    with open(os.path.join('./result/',filename_h),'rb') as f:
        h = pickle.load(f)
    with open(os.path.join('./result/',filename_v),'rb') as f:
        v = pickle.load(f)
    return h,v