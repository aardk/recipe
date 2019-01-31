# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk> 2017
# Aard Keimpema (2019): Call signature of wrapped tasks are now preserved
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

class wrap_casa(object):
  def __init__(self, casatask):
    self.name = casatask.__name__
    self.doc = casatask.__doc__
    self.argspec = inspect.getargspec(casatask)

  def __call__(self, task):
    sp = self.argspec
    narg = len(sp[0])
    ndef = len(sp[3])
    n = narg - ndef # parameters without defaults
    addquotes = lambda x: "'%s'"%(x,) if type(x) == str else x
    argdef = ','.join(sp[0][:n] + ["{}={}".format(sp[0][n+i], addquotes(sp[3][i])) for i in range(ndef)])
    func_def = 'def {name}({argdef}):\n  return task({args})'.format(name = self.name, argdef = argdef, args=','.join(sp[0]))
    print '\n', func_def
    func_ns = {'task': task}
    exec func_def in func_ns
    wrapped_task = func_ns[self.name]
    wrapped_task.__doc__ = self.doc
    wrapped_task.__dict__ = task.__dict__
    wrapped_task.__module__ = task.__module__
    return wrapped_task

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
            "plotms" : "plotfile",
            "concat" : "concatvis"}
    opar=opars[fn.__name__]

    aa=inspect.getcallargs(fn, *args, **kwargs)
    if aa.has_key(opar) and aa[opar] != "" :
        print "Warning: can not supply the output; will be ignored"
    if (fn.__name__ == 'plotms') and (aa['expformat'] == ''):
        aa['expformat'] = 'png'
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
            "setjy": "vis",
            "gaincal" : "caltable",
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

@wrap_casa(casa.ft)
@ccheck
def ft(*args, **kwargs):
    return h_inplc(casa.ft, args, kwargs)

@wrap_casa(casa.gaincal)
@ccheck
def gaincal(*args, **kwargs):
    aa=inspect.getcallargs(casa.gaincal, *args, **kwargs)
    if aa['append'] and os.path.isdir(aa['caltable']):
        return h_inplc(casa.gaincal, args, kwargs)
    else:
        return h_simpo(casa.gaincal, args, kwargs)

@wrap_casa(casa.gencal)
@ccheck
def gencal(*args, **kwargs):
    return h_simpo(casa.gencal, args, kwargs)

@wrap_casa(casa.bandpass)
@ccheck
def bandpass(*args, **kwargs):
    return h_simpo(casa.bandpass, args, kwargs)

@wrap_casa(casa.fringefit)
@ccheck
def fringefit(*args, **kwargs):
    return h_simpo(casa.fringefit, args, kwargs)

@wrap_casa(casa.applycal)
@ccheck
def applycal(*args, **kwargs):
    return h_inplc(casa.applycal, args, kwargs)

@wrap_casa(casa.split)
@ccheck
def split(*args, **kwargs):
    return h_simpo(casa.split, args, kwargs)

@wrap_casa(casa.importuvfits)
@ccheck
def importuvfits(*args, **kwargs):
    return h_simpo(casa.importuvfits, args, kwargs)

@wrap_casa(casa.importfitsidi)
@ccheck
def importfitsidi(*args, **kwargs):
    return h_simpo(casa.importfitsidi, args, kwargs)

@wrap_casa(casa.fixvis)
@ccheck
def fixvis(*args, **kwargs):
    # Note fixvis won't modify input if output is given, so we use it
    # in that mode
    return h_simpo(casa.fixvis, args, kwargs)

@wrap_casa(casa.flagdata)
@ccheck
def flagdata(*args, **kwargs):
    return h_inplc(casa.flagdata, args, kwargs)

@wrap_casa(casa.clean)
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

@wrap_casa(casa.plotms)
@ccheck
def plotms(*args, **kwargs):
    return h_simpo(casa.plotms, args, kwargs)

@wrap_casa(casa.concat)
@ccheck
def concat(*args, **kwargs):
    return h_simpo(casa.concat, args, kwargs)

@wrap_casa(casa.setjy)
@ccheck
def setjy(*args, **kwargs):
    return h_inplc(casa.setjy, args, kwargs)
