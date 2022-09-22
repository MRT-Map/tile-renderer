from __future__ import annotations

import logging
from itertools import chain
from pathlib import Path

from PIL import Image, ImageDraw
from rich.progress import Progress

import renderer.mathtools as mathtools
import renderer.tools as tools
from renderer.types import Coord, TileCoord
from renderer.types.components import Component, ComponentList
from renderer.types.nodes import NodeList
from renderer.types.skin import Skin, _node_list_to_image_coords, _TextObject
from renderer.types.zoom_params import ZoomParams


def _draw_components(
    ph,
    tile_coord: TileCoord,
    tile_components: list[Pla2File],
    all_components: ComponentList,
    nodes: NodeList,
    skin: Skin,
    zoom: ZoomParams,
    assets_dir: Path,
    export_id: str,
) -> tuple[TileCoord, list[_TextObject]]:
    size = zoom.range * 2 ** (zoom.max - tile_coord[0])
    img = Image.new(mode="RGBA", size=(skin.tile_size,) * 2, color=skin.background)
    imd = ImageDraw.Draw(img)
    text_list: list[_TextObject] = []
    points_text_list: list[_TextObject] = []

    for group in tile_components:
        type_info = skin[group[0].type]
        style = type_info[zoom.max - tile_coord[0]]
        for step in style:
            for component in group:
                coords = _node_list_to_image_coords(
                    component.nodes, nodes, skin, tile_coord, size
                )

                args = {
                    "point": {
                        "circle": (imd, coords),
                        "text": (
                            imd,
                            coords,
                            component.displayname,
                            assets_dir,
                            points_text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "square": (imd, coords),
                        "image": (img, coords, assets_dir),
                    },
                    "line": {
                        "text": (
                            imd,
                            img,
                            coords,
                            assets_dir,
                            component,
                            text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "back": (imd, coords),
                        "fore": (imd, coords),
                    },
                    "area": {
                        "bordertext": (
                            imd,
                            coords,
                            component,
                            assets_dir,
                            text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "centertext": (
                            imd,
                            coords,
                            component,
                            assets_dir,
                            text_list,
                            tile_coord,
                            skin.tile_size,
                        ),
                        "fill": (imd, img, coords, component, nodes, tile_coord, size),
                        "centerimage": (img, coords, assets_dir),
                    },
                }

                if step.layer not in args[type_info.shape].keys():
                    raise KeyError(f"{step.layer} is not a valid layer")
                # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}")
                step.render(*args[type_info.shape][step.layer])

                ph.add.remote(tile_coord)

            if (
                type_info.shape == "line"
                and "road" in type_info.tags
                and step.layer == "back"
            ):
                # logger.log("Rendering studs")
                con_nodes: list[str] = list(
                    chain(*(component.nodes for component in group))
                )
                connected: list[tuple[Component, int]] = list(
                    chain(
                        *(
                            tools.nodes.find_components_attached(x, all_components)
                            for x in con_nodes
                        )
                    )
                )
                for con_component, index in connected:
                    if "road" not in skin[con_component.type].tags:
                        continue
                    con_info = skin[con_component.type]
                    for con_step in con_info[zoom.max - tile_coord.z]:
                        if con_step.layer in ["back", "text"]:
                            continue

                        con_coords = _node_list_to_image_coords(
                            con_component.nodes, nodes, skin, tile_coord, size
                        )

                        con_img = Image.new("RGBA", (skin.tile_size,) * 2, (0,) * 4)
                        con_imd = ImageDraw.Draw(con_img)
                        con_step: Skin.ComponentTypeInfo.LineFore
                        con_step.render(con_imd, con_coords)

                        con_mask_img = Image.new(
                            "RGBA", (skin.tile_size,) * 2, (0,) * 4
                        )
                        con_mask_imd = ImageDraw.Draw(con_mask_img)
                        con_mask_imd.ellipse(
                            (
                                con_coords[index].x
                                - (max(con_step.width, step.width) * 2) / 2
                                + 1,
                                con_coords[index].y
                                - (max(con_step.width, step.width) * 2) / 2
                                + 1,
                                con_coords[index].x
                                + (max(con_step.width, step.width) * 2) / 2,
                                con_coords[index].y
                                + (max(con_step.width, step.width) * 2) / 2,
                            ),
                            fill="#000000",
                        )

                        inter = Image.new("RGBA", (skin.tile_size,) * 2, (0,) * 4)
                        inter.paste(con_img, (0, 0), con_mask_img)
                        img.paste(inter, (0, 0), inter)

                ph.add.remote(tile_coord)

    text_list += points_text_list
    text_list.reverse()

    img.save(
        Path(__file__).parent.parent / f"tmp/{export_id}_{tile_coord}.tmp.png", "PNG"
    )
    ph.complete.remote()

    return tile_coord, text_list


def _prevent_text_overlap(
    texts: dict[TileCoord, list[_TextObject]]
) -> dict[TileCoord, list[_TextObject]]:
    out = {}
    with Progress() as progress:
        zoom_id = progress.add_task(
            "[green]Eliminating overlapping text",
            total=len(zooms := set(c.z for c in texts.keys())),
        )
        for z in zooms:
            z: int
            text_dict: dict[_TextObject, list[TileCoord]] = {}
            prep_id = progress.add_task(
                f"Zoom {z}: [dim white]Preparing text", total=len(texts)
            )
            for tile_coord, text_objects in texts.items():
                if tile_coord.z != z:
                    continue
                for text in text_objects:
                    if text not in text_dict:
                        text_dict[text] = []
                    text_dict[text].append(tile_coord)
                progress.advance(prep_id, 1)
            progress.update(prep_id, visible=False)

            no_intersect: list[tuple[Coord]] = []
            operations = len(text_dict)
            filter_id = progress.add_task(
                f"Zoom {z}: [dim white]Filtering text", total=operations
            )
            for i, text in enumerate(text_dict.copy().keys()):
                is_rendered = True
                for other in no_intersect:
                    for bound in text.bounds:
                        if mathtools.poly_intersect(list(bound), list(other)):
                            is_rendered = False
                            del text_dict[text]
                            break
                        if not is_rendered:
                            break
                    if not is_rendered:
                        break
                progress.advance(filter_id, 1)
            progress.update(filter_id, visible=False)

            operations = len(text_dict)
            sort_id = progress.add_task(
                f"Zoom {z}: [dim white]Sorting remaining text", total=operations
            )
            for i, (text, tile_coords) in enumerate(text_dict.items()):
                for tile_coord in tile_coords:
                    if tile_coord not in out:
                        out[tile_coord] = []
                    out[tile_coord].append(text)
                progress.advance(sort_id, 1)

            progress.advance(zoom_id, 1)
        default = {tc: [] for tc in texts.keys()}
    return {**default, **out}


def _draw_text(
    ph,
    tile_coord: TileCoord,
    text_list: list[_TextObject],
    save_images: bool,
    save_dir: Path,
    skin: Skin,
    export_id: str,
) -> dict[TileCoord, Image.Image]:
    logging.getLogger("PIL").setLevel(logging.CRITICAL)
    image = Image.open(
        Path(__file__).parent.parent / f"tmp/{export_id}_{tile_coord}.tmp.png"
    )
    # print(text_list)
    for text in text_list:
        # logger.log(f"Text {processed}/{len(text_list)} pasted")
        for img, center in zip(text.image, text.center):
            image.paste(
                img,
                (
                    int(center.x - tile_coord.x * skin.tile_size - img.width / 2),
                    int(center.y - tile_coord.y * skin.tile_size - img.height / 2),
                ),
                img,
            )
        ph.add.remote(tile_coord)

    # tileReturn[tile_coord] = im
    if save_images:
        image.save(save_dir / f"{tile_coord}.png", "PNG")
    ph.complete.remote()

    return {tile_coord: image}
