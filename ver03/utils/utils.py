import os
import pickle

def preserve(v, filename):
    with open(os.path.join('./result/pkl/',filename+".pkl"), 'wb') as f:
        pickle.dump(v,f)

def Load(filename):
    with open(os.path.join('./result/pkl/',filename),'rb') as f:
        v = pickle.load(f)
    return v
