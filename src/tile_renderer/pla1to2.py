import sys

from rich.console import Console
from rich.progress import track

from tile_renderer._logger import log
from tile_renderer.coord import Coord, Line
from tile_renderer.pla2 import Component, Pla2File


def pla1to2(
    old_comps: dict,
    old_nodes: dict,
) -> list[Pla2File]:
    def get_coord(node: str) -> Coord | None:
        for node_name, node_obj in old_nodes.items():
            if node == node_name:
                return Coord(node_obj["x"], node_obj["y"])
        log.error(f"`{node}` is not found in node lists")
        return None

    comps: dict[str, list[Component]] = {}
    for comp_name, comp in track(old_comps.items(), "Processing PLA 1 components", console=Console(file=sys.stderr)):
        ns = comp_name.split("-")[0]
        id_ = comp_name.removeprefix(ns + "-")
        if "hollows" in comp:
            log.warn(
                f"Hollow data found in `{comp_name}`, PLA 2 doesn't support hollows",
            )
        nodes = Line([a for a in (get_coord(n) for n in comp["nodes"]) if a is not None])
        comps.setdefault(ns, []).append(
            Component(
                namespace=ns,
                id=id_,
                display_name=comp["displayname"],
                description=comp["description"],
                type=comp["type"].split(" ")[0],
                layer=comp["layer"],
                attrs=comp["attrs"],
                tags=comp["type"].split(" ")[1:],
                nodes=nodes,
            ),
        )
    return [Pla2File(namespace=ns, components=comps) for ns, comps in comps.items()]
