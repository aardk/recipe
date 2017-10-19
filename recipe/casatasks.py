"""
Hand-wrapped tasks for CASA
"""

import inspect
from hashlib import sha256

import casa

def hf(fn, *args, **kwargs):
    """Hash a function call, including function name """
    return sha256(fn.func_name+str(inspect.getcallargs(fn, *args, **kwargs))).hexdigest()

def clean(*args, **kwargs):
    return hf(casa.clean, *args, **kwargs)

def split(*args, **kwargs):
    return hf(casa.split, *args, **kwargs)

    
