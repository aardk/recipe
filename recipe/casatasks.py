# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk> 2017
"""
Hand-wrapped tasks for CASA

What we need to do here:
  - For tasks that modify their input, copy them first
  - For tasks with multiple outputs, put them all in a directory
  - For tasks that pickup files from cwd, make sure they don't

Qs:
  - What are the flagversions?
  - The FT model in visibility after CLEAN has the absolute coded path???? Can't move MS?

"""

import inspect, shutil, os
from hashlib import sha256

import casa

import repo

TRACE=True
TRACEV=2

def trc(*args):
    if TRACE: print((" ").join(map(repr, args[0:TRACEV])))

# Decos
def ccheck(fn):
    def newfn(*args, **kwargs):
        hh=hf(getattr(casa, fn.__name__), *args, **kwargs)
        mm=repo.get(hh)
        if mm:
            trc( "[Cached]", fn.__name__, args, kwargs)
            return mm
        else:
            trc( "[Eval] ", fn.__name__, args, kwargs, " -> ", hh)
            tempf=fn(*args,  **kwargs)
            if not os.path.exists(tempf):
                raise RuntimeError("No output produced by " + fn.__name__  + "!")
            return repo.put(tempf, hh)    
    return newfn

# Handlers
def h_simpo(fn, args, kwargs):
    """Simple output task 
    
    All output goes into a single file/dir that is specified
    """
    opars= {"split" : "outputvis",
            "gaincal" : "caltable",
            "importuvfits": "vis",
            "fixvis" : "outputvis"}
    opar=opars[fn.__name__]

    aa=inspect.getcallargs(fn, *args, **kwargs)
    if aa.has_key(opar) and aa[opar] != "" :
        print "Warning: can not supply the output; will be ignored"
    f=repo.mktemp()
    os.remove(f)
    aa[opar]=f
    fn(**aa)
    return f

def h_inplc(fn, args, kwargs):
    """A task that in-place modifies an input

    """
    opars= {"flagdata" : "vis"}
    iopar=opars[fn.__name__]

    aa=inspect.getcallargs(fn, *args, **kwargs)
    f=repo.mktemp()
    os.remove(f)
    shutil.copytree(aa[iopar], f)
    aa[iopar]=f
    fn(**aa)
    return f


# Main part

def hf(fn, *args, **kwargs):
    """Hash a function call, including function name """
    aa=inspect.getcallargs(fn, *args, **kwargs).items(); aa.sort()
    return sha256(fn.func_name+repr(aa)).hexdigest()

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

@ccheck
def fixvis(*args, **kwargs):
    # Note fixvis won't modify input if output is given, so we use it
    # in that mode
    return h_simpo(casa.fixvis, args, kwargs)

@ccheck
def flagdata(*args, **kwargs):
    return h_inplc(casa.flagdata, args, kwargs)

@ccheck
def clean(*args, **kwargs):
    """Clean task

    Clean modifies its input (becuase the model column is updated),
    produces output. Will pick up the clean model if it exists already
    """
    iopar="vis"
    opar="imagename"
    fn=casa.clean
    aa=inspect.getcallargs(fn, *args, **kwargs)
    f=repo.mktemp()
    os.remove(f)
    os.mkdir(f)
    vis=os.path.join(f, "vis")
    shutil.copytree(aa[iopar],vis)
    aa[iopar]=vis
    aa[opar]=os.path.join(f, "img")
    fn(**aa)
    return f    
    
    
    


