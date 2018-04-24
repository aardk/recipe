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
  - Some default parameters get flipped by CASA semi-randomly? E.g., interp for gaincal.

"""

import inspect, shutil, os
from hashlib import sha256
import json

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
            "gencal" : "caltable",
            "bandpass" : "caltable",
            "fringefit" : "caltable",
            "importuvfits": "vis",
            "importfitsidi": "vis",
            "fixvis" : "outputvis",
            "plotms" : "plotfile"}
    opar=opars[fn.__name__]

    aa=inspect.getcallargs(fn, *args, **kwargs)
    if aa.has_key(opar) and aa[opar] != "" :
        print "Warning: can not supply the output; will be ignored"
    f=repo.mktemp()
    # Remove the temporary *file*, but reuse the *filename*.  Do this
    # because CASA won't overwrite and/or needs a directory instead of
    # file
    os.remove(f)
    aa[opar]=f
    fn(**aa)
    return f

def h_inplc(fn, args, kwargs):
    """A task that in-place modifies an input

    """
    opars= {"flagdata" : "vis",
            "ft": "vis",
            "applycal": "vis"}
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
    aa=json.dumps(inspect.getcallargs(fn, *args, **kwargs),
                  sort_keys=True)
    #"for hash: " , fn.func_name+aa
    return sha256(fn.func_name+aa).hexdigest()

@ccheck
def ft(*args, **kwargs):
    return h_inplc(casa.ft, args, kwargs)

@ccheck
def gaincal(*args, **kwargs):
    return h_simpo(casa.gaincal, args, kwargs)

@ccheck
def gencal(*args, **kwargs):
    return h_simpo(casa.gencal, args, kwargs)

@ccheck
def bandpass(*args, **kwargs):
    return h_simpo(casa.bandpass, args, kwargs)

@ccheck
def fringefit(*args, **kwargs):
    return h_simpo(casa.fringefit, args, kwargs)

@ccheck
def applycal(*args, **kwargs):
    return h_inplc(casa.applycal, args, kwargs)

@ccheck
def split(*args, **kwargs):
    return h_simpo(casa.split, args, kwargs)

@ccheck
def importuvfits(*args, **kwargs):
    return h_simpo(casa.importuvfits, args, kwargs)

@ccheck
def importfitsidi(*args, **kwargs):
    return h_simpo(casa.importfitsidi, args, kwargs)

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
    if aa.has_key("phasecenter") and type(aa["phasecenter"])==list and len(aa["phasecenter"]) > 1:
        aa[opar]=[os.path.join(f, "img%i"% ii) for ii in range(len(aa["phasecenter"]))]
    else:
        aa[opar]=os.path.join(f, "img")
    fn(**aa)
    return f

@ccheck
def plotms(*args, **kwargs):
    return h_simpo(casa.plotms, args, kwargs)
