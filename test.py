import sys
from eppy import modeleditor
from eppy.modeleditor import IDF

iddfile = "C:/EnergyPlusV9-4-0/Energy+.idd" 
fname1 = "C:/Users/Eppy/Documents/IDFs/TT_03-26_Test.idf"
IDF.setiddname(iddfile)
idf1 = IDF(fname1)
idf1.printidf()