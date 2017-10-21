RECIPE: Minimal recomputation for radio astronomy
=================================================

This is version 2 of recipe which focuses on memoization. See the PASP
article: Nikolic, Small & Kettenis (2017) "Minimal Re-computation for
Exploratory Data Analysis in Astronomy".


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




