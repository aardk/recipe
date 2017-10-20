"""
Hand-wrapped tasks for CASA

What we need to do here:
  - For tasks that modify their input, copy them first
  - For tasks with multiple outputs, put them all in a directory
  - For tasks that pickup files from cwd, make sure they don't
"""

import inspect, shutil, os
from hashlib import sha256

import casa

import repo

# Decos
def ccheck(fn):
    def newfn(*args, **kwargs):
        hh=hf(getattr(casa, fn.__name__), *args, **kwargs)
        mm=repo.get(hh)
        if mm:
            return mm
        else:
            tempf=fn(*args,  **kwargs)
            return repo.put(tempf, hh)    
    return newfn

# Main part

def hf(fn, *args, **kwargs):
    """Hash a function call, including function name """
    return sha256(fn.func_name+str(inspect.getcallargs(fn, *args, **kwargs))).hexdigest()

def clean(*args, **kwargs):
    return hf(casa.clean, *args, **kwargs)

def split(*args, **kwargs):
    return hf(casa.split, b*args, **kwargs)

@ccheck
def ft(*args, **kwargs):
    aa=inspect.getcallargs(casa.ft, *args, **kwargs)
    f=repo.mktemp()
    os.remove(f)
    shutil.copytree(aa['vis'], f)
    aa['vis']=f
    casa.ft(**aa)
    return f

@ccheck
def gaincal(*args, **kwargs):
    aa=inspect.getcallargs(casa.gaincal, *args, **kwargs)
    if aa.has_key("caltable") and aa["caltable"] != "" :
        print "Warning: can not supply the output; will be ignored"
    f=repo.mktemp()
    os.remove(f)
    aa['caltable']=f
    casa.gaincal(**aa)
    return f

@ccheck
def applycal(*args, **kwargs):
    aa=inspect.getcallargs(casa.applycal, *args, **kwargs)
    f=repo.mktemp()
    os.remove(f)
    shutil.copytree(aa['vis'], f)
    aa['vis']=f
    casa.applycal(**aa)
    return f

@ccheck
def split(*args, **kwargs):
    aa=inspect.getcallargs(casa.split, *args, **kwargs)
    if aa.has_key("outputvis") and aa["outputvis"] != "" :
        print "Warning: can not supply the output; will be ignored"
    f=repo.mktemp()
    os.remove(f)
    aa['outputvis']=f
    casa.split(**aa)
    return f
    



