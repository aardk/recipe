"""
Hand-wrapped tasks for CASA
"""

import inspect, shutil, os
from hashlib import sha256

import casa

import repo

def hf(fn, *args, **kwargs):
    """Hash a function call, including function name """
    return sha256(fn.func_name+str(inspect.getcallargs(fn, *args, **kwargs))).hexdigest()

def clean(*args, **kwargs):
    return hf(casa.clean, *args, **kwargs)

def split(*args, **kwargs):
    return hf(casa.split, b*args, **kwargs)

def ft(*args, **kwargs):
    hh=hf(casa.ft, *args, **kwargs)
    mm=repo.get(hh)
    if mm:
        return mm

    aa=inspect.getcallargs(casa.ft, *args, **kwargs)
    f=repo.mktemp()
    os.remove(f)
    shutil.copytree(aa['vis'], f)
    aa['vis']=f
    casa.ft(**aa)
    return repo.put(f, hh)

def gaincal(*args, **kwargs):
    hh=hf(casa.gaincal, *args, **kwargs)
    mm=repo.get(hh)
    if mm:
        return mm

    aa=inspect.getcallargs(casa.gaincal, *args, **kwargs)
    if aa.has_key("caltable"):
        print "Warning: can not supply the output; will be ignored"
    f=repo.mktemp()
    os.remove(f)
    aa['caltable']=f
    casa.gaincal(**aa)
    return repo.put(f, hh)    
