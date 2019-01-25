# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk> 2017
"""
Repository for recipe values

"""
import os
from hashlib import sha256
import tempfile
import subprocess
import shutil

#REPODIR="/home/user/temp/casa/repo/"
REPODIR = os.path.expanduser('~') + '/casa/repo/'
if not os.path.exists(REPODIR):
  os.makedirs(REPODIR)

# Default is 20GB
EVLIM=20 * (1<<20)
# Evict really?
EVICT=False

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
    # Sets to current time
    os.utime(f, None)

def df(f):
    "Returns number of free bytes"
    f = os.statvfs(str(f))
    return f.f_bavail * f.f_bsize

def evict_m(d):
    """If not enough free space, evict"""
    if (df(d)<EVLIM ):
        al=atimes(d)
        while(len(al) and df(d)<EVLIM):
            x=al.pop(0)[1]
            if EVICT:
                pass
            else:
                print "TRACE: Pretend-removing  " , x

def get(h):
    p=os.path.join(REPODIR, h)
    if os.path.exists(p):
        atouch(p)
        return p
    else:
        return False

def mktemp():
    "Make a temporary file, close the fd"
    fd,n=tempfile.mkstemp(prefix="recipetmp", dir=REPODIR)
    os.close(fd)
    return n

def put(d, h):
    """Put file d at hash h

    :param d: the file to put, it is moved, so won't exist at end of
    operation
    """
    evict_m(REPODIR)
    p=os.path.join(REPODIR, h)
    if os.path.exists(p):
        pass
    else:
        shutil.move(d, p)
    return p
