from _typeshed import Incomplete
from fontTools import cffLib as cffLib
from fontTools import ttLib as ttLib
from fontTools.merge.base import add_method as add_method
from fontTools.merge.base import mergeObjects as mergeObjects
from fontTools.merge.cmap import computeMegaCmap as computeMegaCmap
from fontTools.merge.util import *
from fontTools.ttLib.tables.DefaultTable import DefaultTable as DefaultTable

log: Incomplete
headFlagsMergeBitMap: Incomplete
os2FsTypeMergeBitMap: Incomplete

def mergeOs2FsType(lst): ...
def merge(self, m, tables): ...
