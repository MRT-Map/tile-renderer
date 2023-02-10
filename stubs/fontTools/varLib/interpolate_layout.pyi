from _typeshed import Incomplete
from fontTools.ttLib import TTFont as TTFont
from fontTools.varLib import VarLibError as VarLibError
from fontTools.varLib import load_designspace as load_designspace
from fontTools.varLib import load_masters as load_masters
from fontTools.varLib import models as models
from fontTools.varLib.merger import InstancerMerger as InstancerMerger

log: Incomplete

def interpolate_layout(designspace, loc, master_finder=..., mapped: bool = ...): ...
def main(args: Incomplete | None = ...): ...
