import rich
from rich.progress import track

from tile_renderer.coord import Coord, Line
from tile_renderer.pla2 import Component, Pla2File


def pla1to2(
    old_comps: dict,
    old_nodes: dict,
) -> list[Pla2File]:
    """
    Converts PLA1 to PLA2

    :param old_comps: The components JSON of PLA1
    :param old_nodes: The nodes JSON of PLA1
    """

    def get_coord(node: str) -> Coord:
        for node_name, node_obj in old_nodes.items():
            if node == node_name:
                return Coord(node_obj["x"], node_obj["y"])
        msg = f"`{node}` is not found in node lists"
        raise ValueError(msg)

    comps: dict[str, list[Component]] = {}
    for comp_name, comp in track(old_comps.items(), "Processing PLA 1 components"):
        ns = comp_name.split("-")[0]
        id_ = comp_name.removeprefix(ns + "-")
        if "hollows" in comp:
            rich.print(
                f"[yellow]Hollow data found in `{comp_name}`, PLA 2 doesn't support hollows",
            )
        nodes = Line([get_coord(n) for n in comp["nodes"]])
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
