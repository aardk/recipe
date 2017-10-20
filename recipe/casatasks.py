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
    casa.ft(*args, **kwargs)
    return repo.put(f, hh)
