RECIPE: Minimal recomputation for radio astronomy
=================================================

This is version 2 of recipe which focuses on memoization. See the PASP
article: Nikolic, Small & Kettenis (2017) "Minimal Re-computation for
Exploratory Data Analysis in Astronomy".

How to install
--------------

export CASADIR=/home/user/p/casa-release-5.1.0-74.el7/
wget https://bootstrap.pypa.io/get-pip.py
${CASADIR:? must be set}/bin/python get-pip.py
${CASADIR}/bin/pip2.7 install --upgrade setuptools
${CASADIR:? must be set}/bin/pip install --extra-index-url=https://www.mrao.cam.ac.uk/~bn204/soft/py recipe



How to use
----------

The two main things to remember about how Recipe works:

1. Output will always be contained in a directory returned by the
   function (assign it to a variable!). Any explictly specified output
   will be ignored.

2. If a task modified it's input, the modified input will be in the
   output directory

from recipe import casatasks as c
c.importuvfits(....)
c.clean(....) 

How to contribute
-----------------

git clone http://www.mrao.cam.ac.uk/~bn204/g/recipe/
<work>
git send-email --to="b.nikolic@mrao.cam.ac.uk"


