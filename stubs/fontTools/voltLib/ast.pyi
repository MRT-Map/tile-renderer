from typing import NamedTuple

from _typeshed import Incomplete
from fontTools.voltLib.error import VoltLibError as VoltLibError

class Pos(NamedTuple):
    adv: int
    dx: int
    dy: int
    adv_adjust_by: dict
    dx_adjust_by: dict
    dy_adjust_by: dict

class Element:
    location: Incomplete
    def __init__(self, location: Incomplete | None = ...) -> None: ...
    def build(self, builder) -> None: ...

class Statement(Element): ...
class Expression(Element): ...

class VoltFile(Statement):
    statements: Incomplete
    def __init__(self) -> None: ...
    def build(self, builder) -> None: ...

class GlyphDefinition(Statement):
    name: Incomplete
    id: Incomplete
    unicode: Incomplete
    type: Incomplete
    components: Incomplete
    def __init__(
        self, name, gid, gunicode, gtype, components, location: Incomplete | None = ...
    ) -> None: ...

class GroupDefinition(Statement):
    name: Incomplete
    enum: Incomplete
    glyphs_: Incomplete
    def __init__(self, name, enum, location: Incomplete | None = ...) -> None: ...
    def glyphSet(self, groups: Incomplete | None = ...): ...

class GlyphName(Expression):
    glyph: Incomplete
    def __init__(self, glyph, location: Incomplete | None = ...) -> None: ...
    def glyphSet(self): ...

class Enum(Expression):
    enum: Incomplete
    def __init__(self, enum, location: Incomplete | None = ...) -> None: ...
    def __iter__(self): ...
    def glyphSet(self, groups: Incomplete | None = ...): ...

class GroupName(Expression):
    group: Incomplete
    parser_: Incomplete
    def __init__(self, group, parser, location: Incomplete | None = ...) -> None: ...
    glyphs_: Incomplete
    def glyphSet(self, groups: Incomplete | None = ...): ...

class Range(Expression):
    start: Incomplete
    end: Incomplete
    parser: Incomplete
    def __init__(
        self, start, end, parser, location: Incomplete | None = ...
    ) -> None: ...
    def glyphSet(self): ...

class ScriptDefinition(Statement):
    name: Incomplete
    tag: Incomplete
    langs: Incomplete
    def __init__(self, name, tag, langs, location: Incomplete | None = ...) -> None: ...

class LangSysDefinition(Statement):
    name: Incomplete
    tag: Incomplete
    features: Incomplete
    def __init__(
        self, name, tag, features, location: Incomplete | None = ...
    ) -> None: ...

class FeatureDefinition(Statement):
    name: Incomplete
    tag: Incomplete
    lookups: Incomplete
    def __init__(
        self, name, tag, lookups, location: Incomplete | None = ...
    ) -> None: ...

class LookupDefinition(Statement):
    name: Incomplete
    process_base: Incomplete
    process_marks: Incomplete
    mark_glyph_set: Incomplete
    direction: Incomplete
    reversal: Incomplete
    comments: Incomplete
    context: Incomplete
    sub: Incomplete
    pos: Incomplete
    def __init__(
        self,
        name,
        process_base,
        process_marks,
        mark_glyph_set,
        direction,
        reversal,
        comments,
        context,
        sub,
        pos,
        location: Incomplete | None = ...,
    ) -> None: ...

class SubstitutionDefinition(Statement):
    mapping: Incomplete
    def __init__(self, mapping, location: Incomplete | None = ...) -> None: ...

class SubstitutionSingleDefinition(SubstitutionDefinition): ...
class SubstitutionMultipleDefinition(SubstitutionDefinition): ...
class SubstitutionLigatureDefinition(SubstitutionDefinition): ...
class SubstitutionReverseChainingSingleDefinition(SubstitutionDefinition): ...

class PositionAttachDefinition(Statement):
    coverage: Incomplete
    coverage_to: Incomplete
    def __init__(
        self, coverage, coverage_to, location: Incomplete | None = ...
    ) -> None: ...

class PositionAttachCursiveDefinition(Statement):
    coverages_exit: Incomplete
    coverages_enter: Incomplete
    def __init__(
        self, coverages_exit, coverages_enter, location: Incomplete | None = ...
    ) -> None: ...

class PositionAdjustPairDefinition(Statement):
    coverages_1: Incomplete
    coverages_2: Incomplete
    adjust_pair: Incomplete
    def __init__(
        self, coverages_1, coverages_2, adjust_pair, location: Incomplete | None = ...
    ) -> None: ...

class PositionAdjustSingleDefinition(Statement):
    adjust_single: Incomplete
    def __init__(self, adjust_single, location: Incomplete | None = ...) -> None: ...

class ContextDefinition(Statement):
    ex_or_in: Incomplete
    left: Incomplete
    right: Incomplete
    def __init__(
        self,
        ex_or_in,
        left: Incomplete | None = ...,
        right: Incomplete | None = ...,
        location: Incomplete | None = ...,
    ) -> None: ...

class AnchorDefinition(Statement):
    name: Incomplete
    gid: Incomplete
    glyph_name: Incomplete
    component: Incomplete
    locked: Incomplete
    pos: Incomplete
    def __init__(
        self,
        name,
        gid,
        glyph_name,
        component,
        locked,
        pos,
        location: Incomplete | None = ...,
    ) -> None: ...

class SettingDefinition(Statement):
    name: Incomplete
    value: Incomplete
    def __init__(self, name, value, location: Incomplete | None = ...) -> None: ...
