import functools

from tile_renderer.types.pla2 import Component
from tile_renderer.types.skin import Skin, ComponentStyle, ComponentType, LineBack, LineFore


def render(components: list[Component], skin: Skin, zoom_levels: set[int]):
    for zoom in zoom_levels:
        styling = _get_styling(components, skin, zoom)
        styling = _sort_styling(styling, skin)


def _get_styling(
    components: list[Component], skin: Skin, zoom: int
) -> list[tuple[Component, ComponentType, ComponentStyle, int]]:
    out = []
    for component in components:
        component_type = skin.get_type_by_name(component.type)
        if component_type is None:
            # TODO log
            continue
        styling = component_type.get_styling_by_zoom(zoom)
        if styling is None:
            continue
        for i, style in enumerate(styling):
            out.append((component, component_type, style, i))
    return out


def _sort_styling(
    styling: list[tuple[Component, ComponentType, ComponentStyle, int]], skin: Skin
) -> list[tuple[Component, ComponentType, ComponentStyle, int]]:
    def sort_fn(
        s1: tuple[Component, ComponentType, ComponentStyle, int],
        s2: tuple[Component, ComponentType, ComponentStyle, int],
    ) -> float:
        component1, component_type1, style1, i1 = s1
        component2, component_type2, style2, i2 = s2

        if (delta := component1.layer - component2.layer) != 0:
            return delta

        if "road" in component_type1.tags and "road" in component_type2.tags:
            if isinstance(style1, LineBack) and isinstance(style2, LineFore):
                return -1
            if isinstance(style1, LineFore) and isinstance(style2, LineBack):
                return 1

        if (delta := skin.get_order(component_type1.name) - skin.get_order(component_type2.name)) != 0:
            return delta

        return i1 - i2

    return sorted(styling, key=functools.cmp_to_key(sort_fn))
