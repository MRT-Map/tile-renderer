from fontTools import ttLib as ttLib

def buildVarRegionAxis(axisSupport): ...
def buildVarRegion(support, axisTags): ...
def buildVarRegionList(supports, axisTags): ...
def VarData_calculateNumShorts(self, optimize: bool = ...): ...
def VarData_CalculateNumShorts(self, optimize: bool = ...): ...
def VarData_optimize(self): ...
def buildVarData(varRegionIndices, items, optimize: bool = ...): ...
def buildVarStore(varRegionList, varDataList): ...
def buildVarIdxMap(varIdxes, glyphOrder): ...
def buildDeltaSetIndexMap(varIdxes): ...
def buildVarDevTable(varIdx): ...
