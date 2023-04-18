from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw

from ..misc_types.coord import ImageCoord, TileCoord
from ..misc_types.pla2 import Component
from ..render.text_object import TextObject
from . import ComponentStyle

if TYPE_CHECKING:
    from ..misc_types.config import Config
    from ..render.part1 import Part1Consts


class AreaBorderText(ComponentStyle):
    """Represent the border text of an area. Will be rendered in the future"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_, **__):
        self.tags = tags
        self.layer = "bordertext"
        self.colour: str | None = json["colour"]
        self.offset: int = json["offset"]
        self.size: int = json["size"]

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ):
        pass

    def text(
        self, component: Component, imd: ImageDraw.ImageDraw, config: Config, zoom: int
    ) -> list[TextObject]:
        return []

        # TODO fix
        """
        if len(component.display_name.strip()) == 0:
            return
        font = config.skin.get_font(
            "", self.size + 2, assets_dir, component.display_name
        )
        text_length = int(
            imd.textlength(component.display_name.replace("\n", ""), font)
        )
        for c1, c2 in internal._with_next(coords.coords):
            if coords.in_bounds(
                Bounds(
                    x_min=0,
                    x_max=config.skin.tile_size,
                    y_max=config.skin.tile_size,
                    y_min=0,
                )
            ) and 2 * text_length <= c1.point.distance(c2.point):
                t = math.floor(c1.point.distance(c2.point) / (4 * text_length))
                t = 1 if t == 0 else t
                all_points: list[
                    list[tuple[ImageCoord, float]]
                ] = math_utils.midpoint(
                    c1, c2, self.offset, n=t, return_both=True
                )
                for n in range(0, len(all_points), 2):
                    p1, p2 = all_points[n][0], all_points[n][1]
                    if self.offset < 0:
                        (tx, ty), trot = (
                            p1
                            if not math_utils.point_in_poly(
                                p1[0].x, p1[0].y, coords
                            )
                            else p2
                        )
                    else:
                        (tx, ty), trot = (
                            p1
                            if math_utils.point_in_poly(
                                p1[0].x, p1[0].y, coords
                            )
                            else p2
                        )
                    abt_i = Image.new(
                        "RGBA",
                        (2 * text_length, 2 * (self.size + 4)),
                        (0, 0, 0, 0),
                    )
                    abt_d = ImageDraw.Draw(abt_i)
                    abt_d.text(
                        (text_length, self.size + 4),
                        component.display_name.replace("\n", ""),
                        fill=self.colour,
                        font=font,
                        anchor="mm",
                        stroke_width=1,
                        stroke_fill="#dddddd",
                        spacing=1,
                    )
                    tw, th = abt_i.size[:]
                    abt_ir = abt_i.rotate(trot, expand=True)
                    abt_ir = abt_ir.crop((0, 0, abt_ir.width, abt_ir.height))
                    text_list.append(
                        TextObject(
                            abt_ir,
                            tx,
                            ty,
                            tw / 2,
                            th / 2,
                            trot,
                            tile_coord,
                            tile_size,
                            imd,
                            ,
                temp_dir=temp_dir,
                export_id=export_id
                        )
                    )"""


class AreaCenterText(ComponentStyle):
    """Represents the text at the centre of an area"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_, **__):
        self.tags = tags
        self.layer = "centertext"
        self.colour: str | None = json["colour"]
        self.offset: ImageCoord = ImageCoord(*json["offset"])
        self.size: int = json["size"]

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ):
        pass

    def text(
        self, component: Component, imd: ImageDraw.ImageDraw, config: Config, zoom: int
    ) -> list[TextObject]:
        coords = component.nodes.to_image_line(TileCoord(zoom, 0, 0), config)
        if len(component.display_name.strip()) == 0:
            return []
        c = ImageCoord(
            coords.centroid.x + self.offset.x, coords.centroid.y + self.offset.y
        )
        font = config.skin.get_font(
            "", self.size + 2, config.assets_dir, component.display_name
        )
        text_length = int(
            min(
                imd.textlength(x.strip(), font)
                for x in component.display_name.split("\n")
            )
        )

        left = min(cl.x for cl in coords)
        right = max(cr.x for cr in coords)
        delta = right - left
        if text_length > delta:
            # logger.log(f"{style.index(self) + 1}/{len(style)} {component.name}: Breaking up string")
            tokens = component.display_name.split()
            wss = re.findall(r"\s+", component.display_name)
            text = ""
            for token, ws in list(itertools.zip_longest(tokens, wss, fillvalue="")):
                temp_text = text[:]
                temp_text += token
                if int(imd.textlength(temp_text.split("\n")[-1], font)) > delta:
                    text += "\n" + token + ws
                else:
                    text += token + ws
            text_length = int(
                max(imd.textlength(x.strip(), font) for x in text.split("\n"))
            )
            text_size = int(imd.textsize(text, font)[1] * 2)
        else:
            text = component.display_name
            text_size = self.size * 2

        act_i = Image.new("RGBA", (2 * text_length, 2 * text_size), (0, 0, 0, 0))
        act_d = ImageDraw.Draw(act_i)
        act_d.multiline_text(
            (text_length, text_size),
            "\n".join(x.strip() for x in text.split("\n")),
            fill=self.colour,
            font=font,
            anchor="mm",
            stroke_width=1,
            stroke_fill="#dddddd",
            align="center",
            spacing=-self.size / 2,
        )
        act_i = act_i.crop((0, 0, act_i.width, act_i.height))
        return [TextObject(act_i, c, (text_length, text_size), 0, zoom, config)]


class AreaFill(ComponentStyle):
    """Represents the fill and outline of an area"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_, **__):
        self.tags = tags
        self.layer = "fill"
        self.colour: str | None = json["colour"]
        self.outline: str | None = json["outline"]
        self.stripe: tuple[int, int, int] | None = (  # type: ignore
            None if json["stripe"] is None else tuple(json["stripe"])  # type: ignore
        )  # TODO find way to typecheck this

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ):
        coords = component.nodes.to_image_line(tile_coord, consts)
        ai = Image.new(
            "RGBA",
            (consts.skin.tile_size, consts.skin.tile_size),
            (0, 0, 0, 0),
        )
        ad = ImageDraw.Draw(ai)

        if self.stripe is not None:
            # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Generating stripes")
            bounds = coords.bounds
            bounds.x_max += bounds.x_max - bounds.x_min
            bounds.x_min -= bounds.y_max - bounds.y_min
            bounds.y_max += bounds.x_max - bounds.x_min
            bounds.y_min -= bounds.y_max - bounds.y_min
            af_i = Image.new(
                "RGBA",
                (
                    consts.skin.tile_size,
                    consts.skin.tile_size,
                ),
                (0, 0, 0, 0),
            )
            af_d = ImageDraw.Draw(af_i)
            tlx = bounds.x_min - 1
            while tlx <= bounds.x_max:
                af_d.polygon(
                    [
                        (tlx, bounds.y_min),
                        (tlx + self.stripe[0], bounds.y_min),
                        (tlx + self.stripe[0], bounds.y_max),
                        (tlx, bounds.y_max),
                    ],
                    fill=self.colour,
                )
                tlx += self.stripe[0] + self.stripe[1]
            af_i = af_i.rotate(
                self.stripe[2], center=(coords.centroid.x, coords.centroid.y)
            )
            mi = Image.new(
                "RGBA",
                (
                    consts.skin.tile_size,
                    consts.skin.tile_size,
                ),
                (0, 0, 0, 0),
            )
            md = ImageDraw.Draw(mi)
            md.polygon([c.as_tuple() for c in coords.coords], fill=self.colour)
            pi = Image.new(
                "RGBA",
                (
                    consts.skin.tile_size,
                    consts.skin.tile_size,
                ),
                (0, 0, 0, 0),
            )
            pi.paste(af_i, (0, 0), mi)
            ai.paste(pi, (0, 0), pi)
        else:
            # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Filling area")
            ad.polygon(
                [c.as_tuple() for c in coords.coords],
                fill=self.colour,
                outline=self.outline,
            )

        """if component.hollows is not None:
            for n in component.hollows:
                n_coords = _node_list_to_image_coords(
                    n, nodes, config.skin, tile_coord, size
                )
                ad.polygon(n_coords, fill=(0, 0, 0, 0))       """
        img.paste(ai, (0, 0), ai)

        if self.outline is not None:
            # logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Drawing outline")
            exterior_outline = coords.coords[:]
            exterior_outline.append(exterior_outline[0])
            outlines = [exterior_outline]
            """if component.hollows is not None:
                for n in component.hollows:
                    n_coords = _node_list_to_image_coords(
                        n, nodes, config.skin, tile_coord, size
                    )
                    n_coords.append(n_coords[0])
                    outlines.append(n_coords)  """
            for o_coords in outlines:
                imd.line(
                    [c.as_tuple() for c in o_coords],
                    fill=self.outline,
                    width=2,
                    joint="curve",
                )


class AreaCenterImage(ComponentStyle):
    """Represents the image at the centre of an area"""

    # noinspection PyInitNewSignature
    def __init__(self, json: dict, tags: list[str], *_, **__):
        self.tags = tags
        self.layer = "centerimage"
        self.file: Path = Path(json["file"])
        self.offset: ImageCoord = ImageCoord(*json["offset"])

    def render(
        self,
        component: Component,
        imd: ImageDraw.ImageDraw,
        img: Image.Image,
        consts: Part1Consts,
        tile_coord: TileCoord,
    ):
        coords = component.nodes.to_image_line(tile_coord, consts)
        cx, cy = (coords.centroid.x, coords.centroid.y)
        icon = Image.open(consts.assets_dir / self.file)
        img.paste(icon, (int(cx + self.offset.x), int(cy + self.offset.y)), icon)
