# Bojan Nikolic <b.nikolic@mrao.cam.ac.uk> 2017

from distutils.core import setup
import glob

setup(
    name = "recipe",
    version = "0.1",
    packages = ['recipe'],
    scripts = glob.glob("test/*.py"),
    author = "Bojan Nikolic",
    author_email = "b.nikolic@mrao.cam.ac.uk",
    description = "Minimial recomputation engine for the NRAO CASA package",
    license = "GPL",
    url = "http://www.mrao.cam.ac.uk/~bn204/",    
    )
    
