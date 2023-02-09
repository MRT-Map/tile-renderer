from _typeshed import Incomplete
from fontTools.subset.cff import *
from fontTools.subset.svg import *

class Options:
    class OptionError(Exception): ...
    class UnknownOptionError(OptionError): ...
    drop_tables: Incomplete
    no_subset_tables: Incomplete
    passthrough_tables: bool
    hinting_tables: Incomplete
    legacy_kern: bool
    layout_closure: bool
    layout_features: Incomplete
    layout_scripts: Incomplete
    ignore_missing_glyphs: bool
    ignore_missing_unicodes: bool
    hinting: bool
    glyph_names: bool
    legacy_cmap: bool
    symbol_cmap: bool
    name_IDs: Incomplete
    name_legacy: bool
    name_languages: Incomplete
    obfuscate_names: bool
    retain_gids: bool
    notdef_glyph: bool
    notdef_outline: bool
    recommended_glyphs: bool
    recalc_bounds: bool
    recalc_timestamp: bool
    prune_unicode_ranges: bool
    recalc_average_width: bool
    recalc_max_context: bool
    canonical_order: Incomplete
    flavor: Incomplete
    with_zopfli: bool
    desubroutinize: bool
    harfbuzz_repacker: Incomplete
    verbose: bool
    timing: bool
    xml: bool
    font_number: int
    pretty_svg: bool
    lazy: bool
    def __init__(self, **kwargs) -> None: ...
    def set(self, **kwargs) -> None: ...
    def parse_opts(self, argv, ignore_unknown=...): ...

class Subsetter:
    class SubsettingError(Exception): ...
    class MissingGlyphsSubsettingError(SubsettingError): ...
    class MissingUnicodesSubsettingError(SubsettingError): ...
    options: Incomplete
    unicodes_requested: Incomplete
    glyph_names_requested: Incomplete
    glyph_ids_requested: Incomplete
    def __init__(self, options: Incomplete | None = ...) -> None: ...
    def populate(self, glyphs=..., gids=..., unicodes=..., text: str = ...) -> None: ...
    def subset(self, font) -> None: ...

def load_font(
    fontFile,
    options,
    checkChecksums: int = ...,
    dontLoadGlyphNames: bool = ...,
    lazy: bool = ...,
): ...
def save_font(font, outfile, options) -> None: ...
def parse_unicodes(s): ...
def parse_gids(s): ...
def parse_glyphs(s): ...
def main(args: Incomplete | None = ...): ...
