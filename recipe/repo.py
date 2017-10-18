"""
Repository for recipe values
"""
import os
from hashlib import sha256
import tempfile
import subprocess
import shutil

# Default is 20GB
EVLIM=20 * (1<<20)

def atimes(d):
    """
    Returns in ascending order (so least recently accessed is first)
    """
    
    res=[]
    def ww(fl):
        for f in fl:
            ff=os.path.join(d, f)
            res.append( (os.stat(ff).st_atime, ff) )
    ww(os.listdir(d))
    res.sort()
    return res

def atouch(f):
    if os.path.isdir(f):
        print "Don't know how to set directory atime"
        tempfile.TemporaryFile(dir=f).close()
    else:
        open(f, "r").close()

def df(f):
    "Returns number of free blocks"
    x=subprocess.check_output(["df", "--output=avail", str(f)]).split()
    # Output on second line
    return int(x[1])

def evict_m(d):
    """If not enough free space, evict"""
    if (df(d)<EVLIM ):
        al=atimes(d)
        while(len(al) and df(d)<EVLIM):
            x=al.pop(0)[1]
            print "Removing" , x
