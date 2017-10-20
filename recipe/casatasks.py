# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk> 2017
"""
Hand-wrapped tasks for CASA

What we need to do here:
  - For tasks that modify their input, copy them first
  - For tasks with multiple outputs, put them all in a directory
  - For tasks that pickup files from cwd, make sure they don't

Qs:
  - What are the flagversions?

"""

import inspect, shutil, os
from hashlib import sha256

import casa

import repo

TRACE=True

# Decos
def ccheck(fn):
    def newfn(*args, **kwargs):
        hh=hf(getattr(casa, fn.__name__), *args, **kwargs)
        mm=repo.get(hh)
        if mm:
            if TRACE : print "TRACE: Using cached value of:", fn.__name__, args, kwargs
            return mm
        else:
            if TRACE : print "TRACE: Calculating value of:", fn.__name__, args, kwargs
            tempf=fn(*args,  **kwargs)
            return repo.put(tempf, hh)    
    return newfn

# Handlers
def h_simpo(fn, args, kwargs):
    """Simple output task 
    
    All output goes into a single file/dir that is specified
    """
    opars= {"split" : "outputvis",
            "gaincal" : "caltable",
            "importuvfits": "vis"}
    opar=opars[fn.__name__]

    aa=inspect.getcallargs(fn, *args, **kwargs)
    if aa.has_key(opar) and aa[opar] != "" :
        print "Warning: can not supply the output; will be ignored"
    f=repo.mktemp()
    os.remove(f)
    aa[opar]=f
    fn(**aa)
    return f    

# Main part

def hf(fn, *args, **kwargs):
    """Hash a function call, including function name """
    return sha256(fn.func_name+str(inspect.getcallargs(fn, *args, **kwargs))).hexdigest()

def clean(*args, **kwargs):
    return hf(casa.clean, *args, **kwargs)

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
    return h_simpo(casa.gaincal, args, kwargs)    

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
    return h_simpo(casa.split, args, kwargs)

@ccheck
def importuvfits(*args, **kwargs):
    return h_simpo(casa.importuvfits, args, kwargs)

    



