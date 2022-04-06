from __future__ import annotations

import itertools
import math
import re
from copy import copy
from dataclasses import dataclass
from typing import Literal
from pathlib import Path

import blessed
import imagehash
from PIL import ImageFont, ImageDraw, Image
from schema import Schema, And, Or, Regex, Optional

import renderer.internals.internal as internal
from renderer import mathtools
from renderer import tools
from renderer.objects.components import Component
from renderer.objects.nodes import NodeList
from renderer.types import RealNum, SkinJson, SkinType, Coord, TileCoord

Image.Image.__hash__ = lambda self: int(str(imagehash.average_hash(self)), base=16)

@dataclass(eq=True, unsafe_hash=True)
class _TextObject:
    image: tuple[Image.Image, ...]
    center: tuple[Coord, ...]
    bounds: tuple[tuple[Coord, ...]]

    def __init__(self, image: Image.Image,
                 x: RealNum, y: RealNum,
                 w: RealNum, h: RealNum,
                 rot: RealNum,
                 tile_coord: TileCoord,
                 tile_size: int,
                 imd: ImageDraw,
                 debug: bool = False):
        r = lambda a, b: mathtools.rotate_around_pivot(a, b,
                                                       tile_coord.x * tile_size + x,
                                                       tile_coord.y * tile_size + y,
                                                       -rot)
        self.image = (image,)
        self.center = (Coord(tile_coord.x * tile_size + x, tile_coord.y * tile_size + y),)
        self.bounds = ((
            r(tile_coord.x * tile_size + x - w / 2, tile_coord.y * tile_size + y - h / 2),
            r(tile_coord.x * tile_size + x - w / 2, tile_coord.y * tile_size + y + h / 2),
            r(tile_coord.x * tile_size + x + w / 2, tile_coord.y * tile_size + y + h / 2),
            r(tile_coord.x * tile_size + x + w / 2, tile_coord.y * tile_size + y - h / 2),
            r(tile_coord.x * tile_size + x - w / 2, tile_coord.y * tile_size + y - h / 2),
        ),)
        if debug:
            nr = lambda a, b: mathtools.rotate_around_pivot(a, b, x, y, -rot)
            imd.line([
                nr(x - w / 2, y - h / 2),
                nr(x - w / 2, y + h / 2),
                nr(x + w / 2, y + h / 2),
                nr(x + w / 2, y - h / 2),
                nr(x - w / 2, y - h / 2)
            ], fill="#ff0000")

    @classmethod
    def from_multiple(cls, *textobject: _TextObject):
        to = copy(textobject[0])

        to.bounds = tuple(itertools.chain(*[sto.bounds for sto in textobject]))
        to.image = tuple(itertools.chain(*[sto.image for sto in textobject]))
        to.center = tuple(itertools.chain(*[sto.center for sto in textobject]))

        return to


def _node_list_to_image_coords(node_list: list[str], nodes: NodeList, skin: Skin, tile_coord: TileCoord, size: RealNum) -> list[Coord]:
    image_coords = []
    for x, y in tools.nodes.to_coords(node_list, nodes):
        xc = x - tile_coord.x * size
        yc = y - tile_coord.y * size
        xs = int(skin.tile_size / size * xc)
        ys = int(skin.tile_size / size * yc)
        image_coords.append(Coord(xs, ys))
    return image_coords

class Skin:
    """Represents a skin.

    :param SkinJson json: The JSON of the skin."""
    def __init__(self, json: SkinJson):
        self.validate_json(json)
        self.tile_size: int = json['info']['size']
        self.fonts: dict[str, Path] = {name: Path(path) for name, path in json['info']['font'].items()}
        self.background: str = json['info']['background']

        self.order: list[str] = json['order']
        self.types: dict[str, Skin.ComponentTypeInfo] \
            = {name: self.ComponentTypeInfo(name, value, self.order, self) for name, value in json['types'].items()}

    def __getitem__(self, type_name: str) -> ComponentTypeInfo:
        return self.types[type_name]

    def get_font(self, style: str, size: int, assets_dir: Path) -> ImageFont.FreeTypeFont:
        """Gets a font, given the style and size.

        :param str style: The style of the font needed, eg. bold, italic etc
        :param int size: The size of the font
        :param Path assets_dir: Where the font is stored
        :return: The font
        :rtype: ImageFont.FreeTypeFont
        :raises FileNotFoundError: if font is not found"""
        if style in self.fonts.keys():
            return ImageFont.truetype(str(assets_dir/self.fonts[style]), size)
        raise FileNotFoundError(f"Font for {style} not found")

    class ComponentTypeInfo:
        """An object representing a component type in the ``types`` portion of a skin.

        :param str name: Will set  ``name``
        :param SkinType json: The JSON of the component type
        :param list[str] order: Will set ``_order``"""
        def __init__(self, name: str, json: SkinType, order: list[str], skin: Skin):
            self.name: str = name
            """The name of the component."""
            self.tags: list[str] = json['tags']
            """The list of tags attributed to the component."""
            self.shape: Literal["point", "line", "area"] = json['type']
            """The shape of the component, must be one of ``point``, ``line``, ``area``"""
            self._order = order
            self._skin = skin
            self.styles: dict[tuple[int, int], list[Skin.ComponentTypeInfo.ComponentStyle]] \
                = {internal._str_to_tuple(range_): [self.ComponentStyle(v, self, shape=self.shape) for v in value] for range_, value in json['style'].items()}
            """The styles of the object, denoted as ``{(max_zoom, min_zoom): [style, ...]}``"""

        def __getitem__(self, zoom_level: int) -> list[ComponentStyle]:
            for (max_level, min_level), styles in self.styles.items():
                if max_level <= zoom_level <= min_level:
                    return styles
            else:
                return []
        
        class ComponentStyle:
            """Represents the ``styles`` portion of a ComponentTypeInfo. Base class for all types of ComponentStyle.

            :param dict json: JSON dictionary as input
            :param CompnentTypeInfo type_info: The type_info that the ComponentStyle is under"""
            def __new__(cls, json: dict | None = None, type_info: Skin.ComponentTypeInfo | None = None, shape: Literal["point", "line", "area"] | None = None):
                if cls != Skin.ComponentTypeInfo.ComponentStyle: return super().__new__(cls)
                if shape == "point":
                    if json['layer'] == "circle": return Skin.ComponentTypeInfo.PointCircle.__new__(Skin.ComponentTypeInfo.PointCircle, json, type_info)
                    if json['layer'] == "text": return Skin.ComponentTypeInfo.PointText.__new__(Skin.ComponentTypeInfo.PointText, json, type_info)
                    if json['layer'] == "square": return Skin.ComponentTypeInfo.PointSquare.__new__(Skin.ComponentTypeInfo.PointSquare, json, type_info)
                    if json['layer'] == "image": return Skin.ComponentTypeInfo.PointImage.__new__(Skin.ComponentTypeInfo.PointImage, json, type_info)
                elif shape == "line":
                    if json['layer'] == "text": return Skin.ComponentTypeInfo.LineText.__new__(Skin.ComponentTypeInfo.LineText, json, type_info)
                    if json['layer'] == "back": return Skin.ComponentTypeInfo.LineBack.__new__(Skin.ComponentTypeInfo.LineBack, json, type_info)
                    if json['layer'] == "fore": return Skin.ComponentTypeInfo.LineFore.__new__(Skin.ComponentTypeInfo.LineFore, json, type_info)
                elif shape == "area":
                    if json['layer'] == "bordertext": return Skin.ComponentTypeInfo.AreaBorderText.__new__(Skin.ComponentTypeInfo.AreaBorderText, json, type_info)
                    if json['layer'] == "centertext": return Skin.ComponentTypeInfo.AreaCenterText.__new__(Skin.ComponentTypeInfo.AreaCenterText, json, type_info)
                    if json['layer'] == "fill": return Skin.ComponentTypeInfo.AreaFill.__new__(Skin.ComponentTypeInfo.AreaFill, json, type_info)
                    if json['layer'] == "centerimage": return Skin.ComponentTypeInfo.AreaCenterImage.__new__(Skin.ComponentTypeInfo.AreaCenterImage, json, type_info)
                raise ValueError(f"No layer `{json['layer']}` in shape `{shape}`")

            def render(self, *args, **kwargs):
                """Renders the component into an ImageDraw instance."""

        class PointCircle(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "circle"
                self.colour: str | None = json['colour']
                self.outline: str | None = json['outline']
                self.size: int = json['size']
                self.width: int = json['width']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord], **_):
                imd.ellipse((coords[0].x - self.size / 2 + 1,
                             coords[0].y - self.size / 2 + 1,
                             coords[0].x + self.size / 2,
                             coords[0].y + self.size / 2),
                            fill=self.colour, outline=self.outline, width=self.width)

        class PointText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "text"
                self.colour: str | None = json['colour']
                self.size: int = json['size']
                self.offset: Coord = Coord(*json['offset'])
                self.anchor: str = json['anchor']
                
            def render(self, imd: ImageDraw, coords: list[Coord], 
                       displayname: str, assets_dir: Path, points_text_list: list[_TextObject],
                       tile_coord: TileCoord, tile_size: int, debug: bool = False):
                if len(displayname.strip()) == 0: return
                font = self._type_info._skin.get_font("", self.size+2, assets_dir)
                text_length = int(imd.textlength(displayname, font))
                pt_i = Image.new('RGBA', (2 * text_length, 2 * (self.size + 4)), (0, 0, 0, 0))
                pt_d = ImageDraw.Draw(pt_i)
                pt_d.text((text_length, self.size + 4), displayname, fill=self.colour, font=font,
                          anchor="mm", stroke_width=1, stroke_fill="#dddddd")
                tw, th = pt_i.size
                pt_i = pt_i.crop((0, 0, pt_i.width, pt_i.height))
                points_text_list.append(_TextObject(pt_i,
                                                    coords[0].x + self.offset[0],
                                                    coords[0].y + self.offset[1],
                                                    tw/2, th/2, 0,
                                                    tile_coord, tile_size,
                                                    imd, debug=debug))
                #font = skin.get_font("", step.size)
                #img.text((coords[0][0]+step.offset[0], coords[0][1]+step.offset[1]), component.displayname, fill=step.colour, font=font, anchor=step['anchor'])
            
        class PointSquare(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "square"
                self.colour: str | None = json['colour']
                self.outline: str | None = json['outline']
                self.size: int = json['size']
                self.width: int = json['width']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord], **_):
                imd.rectangle((coords[0].x - self.size / 2 + 1,
                               coords[0].y - self.size / 2 + 1,
                               coords[0].x + self.size / 2,
                               coords[0].y + self.size / 2),
                              fill=self.colour, outline=self.outline, width=self.width)

        class PointImage(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "image"
                self.file: Path = Path(json['file'])
                self.offset: Coord = Coord(*json['offset'])
                
            def render(self, img: Image.Image, coords: list[Coord],
                       assets_dir: Path, **_):
                icon = Image.open(assets_dir/self.file)
                img.paste(icon, (int(coords[0].x - icon.width / 2 + self.offset[0]),
                                 int(coords[0].y - icon.height / 2 + self.offset[1])), icon)

        class LineText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info: Skin.ComponentTypeInfo = type_info
                self.layer = "text"
                self.arrow_colour: str | None = json['arrow_colour']
                self.colour: str | None = json['colour']
                self.size: int = json['size']
                self.offset: int = json['offset']

            def _text_on_line(self, imd: ImageDraw.ImageDraw, img: Image.Image,
                              font: ImageFont.FreeTypeFont,
                              text: str, coords: list[Coord],
                              tile_coord: TileCoord, tile_size: int,
                              fill: str | None = None, stroke: str | None = None,
                              debug: bool = False, paste_direct: bool = False,
                              upright: bool = True) -> _TextObject | None:
                char_cursor = 0
                text_to_print = ""
                overflow = 0
                text_objects = []
                swap = coords[-1].x < coords[0].x
                if swap and upright: coords = coords[::-1]
                for c1, c2 in internal._with_next(coords):
                    if c2 == coords[-1]:
                        while char_cursor < len(text):
                            text_to_print += text[char_cursor]
                            char_cursor += 1
                    else:
                        while overflow + imd.textlength(text_to_print, font) < math.dist(c1, c2)\
                                and char_cursor < len(text):
                            text_to_print += text[char_cursor]
                            char_cursor += 1
                    if char_cursor != len(text):
                        text_to_print = text_to_print[:-1]
                        char_cursor -= 1
                    text_length = int(imd.textlength(text_to_print, font))

                    if text_length != 0:
                        lt_i = Image.new('RGBA', (2 * text_length, 2 * (self.size + 4)), (0, 0, 0, 0))
                        lt_d = ImageDraw.Draw(lt_i)
                        lt_d.text((text_length, self.size + 4), text_to_print,
                                  fill=fill or self.colour, font=font, anchor="mm",
                                  stroke_width=1, stroke_fill=stroke or "#dddddd")
                        tw, th = lt_i.size[:]
                        trot = math.atan2(-c2.y+c1.y, c2.x-c1.x)/math.pi*180
                        lt_i = lt_i.rotate(trot, expand=True)
                        lt_i = lt_i.crop((0, 0, lt_i.width, lt_i.height))
                        tx = c2.x - ((c2.x-c1.x - overflow * math.cos(trot/180*math.pi)) / 2)
                        ty = c2.y - ((c2.y-c1.y - overflow * math.sin(trot/180*math.pi)) / 2)
                        if paste_direct:
                            img.paste(lt_i, (int(tx-lt_i.width/2), int(ty-lt_i.height/2)), lt_i)
                            if debug:
                                nr = lambda a, b: mathtools.rotate_around_pivot(a, b, tx, ty, -trot)
                                imd.line([
                                    nr(tx - tw / 4, ty - th / 4),
                                    nr(tx - tw / 4, ty + th / 4),
                                    nr(tx + tw / 4, ty + th / 4),
                                    nr(tx + tw / 4, ty - th / 4),
                                    nr(tx - tw / 4, ty - th / 4)
                                ], fill="#ff0000")
                        else:
                            text_objects.append(_TextObject(lt_i, tx, ty,
                                                            tw/2, th/2, trot,
                                                            tile_coord, tile_size, imd, debug=debug))

                    text_to_print = ""
                    overflow = text_length - (math.dist(c1, c2) - overflow)

                    if char_cursor >= len(text): break
                if text_objects: return _TextObject.from_multiple(*text_objects)
                else: return None

            def render(self, imd: ImageDraw.ImageDraw, img: Image.Image, coords: list[Coord],
                       assets_dir: Path, component: Component, text_list: list[_TextObject],
                       tile_coord: TileCoord, tile_size: int, debug: bool = False):
                if len(component.displayname) == 0: return
                #logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Calculating text length")
                font = self._type_info._skin.get_font("", self.size+2, assets_dir)
                text_length = int(imd.textlength(component.displayname, font))
                if text_length == 0:
                    text_length = int(imd.textlength("----------", font))

                coord_lines = mathtools.combine_edge_dashes(mathtools.dash(
                    mathtools.offset(coords, self.offset), text_length, text_length*1.5))
                if coord_lines \
                   and sum(math.dist(c1, c2) for c1, c2 in internal._with_next(coord_lines[-1])) < text_length:
                    coord_lines = coord_lines[:-1]
                if debug:
                    imd.line(mathtools.offset(coords, self.offset), fill="#ff0000")
                text_list.extend(filter(lambda e: e is not None,
                                        (self._text_on_line(imd, img, font, component.displayname,
                                                            list(cs), tile_coord, tile_size, debug=debug)
                                         for cs in coord_lines)))

                if 'oneWay' in component.tags:
                    arrow_coord_lines = mathtools.combine_edge_dashes(mathtools.dash(
                        mathtools.offset(coords, self.offset+self.size*3/16), text_length/2, text_length*0.75
                    ))
                    if arrow_coord_lines \
                       and sum(math.dist(c1, c2) for c1, c2 in internal._with_next(arrow_coord_lines[-1])) \
                       < int(imd.textlength("→", font)):
                        arrow_coord_lines = arrow_coord_lines[:-1]
                    text_list.extend(filter(lambda e: e is not None,
                                            (self._text_on_line(imd, img, font, "→",
                                                                list(cs), tile_coord, tile_size,
                                                                fill=self.arrow_colour, stroke="#00000000",
                                                                debug=debug, paste_direct=True, upright=False)
                                             for i, cs in enumerate(arrow_coord_lines) if i % 2 != 0)))
               
        class LineBack(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "back"
                self.colour: str | None = json['colour']
                self.width: int = json['width']
                self.dash: tuple[int, int] = json['dash']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord], **_):
                if self.dash is None:
                    imd.line(coords, fill=self.colour, width=self.width, joint="curve")
                    if "unroundedEnds" not in self._type_info.tags:
                        imd.ellipse([coords[0].x - self.width / 2+1, coords[0].y - self.width / 2+1,
                                     coords[0].x + self.width / 2-1, coords[0].y + self.width / 2-1],
                                    fill=self.colour)
                        imd.ellipse([coords[-1].x - self.width / 2+1, coords[-1].y - self.width / 2+1,
                                     coords[-1].x + self.width / 2-1, coords[-1].y + self.width / 2-1],
                                    fill=self.colour)
                else:
                    for dash_coords in mathtools.dash(coords, self.dash[0], self.dash[1]):
                        imd.line(dash_coords, fill=self.colour, width=self.width)
                
        class LineFore(LineBack):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                super().__init__(json, type_info)
                self.layer = "fore"

        class AreaBorderText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "bordertext"
                self.colour: str | None = json['colour']
                self.offset: int = json['offset']
                self.size: int = json['size']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord], component: Component,
                       assets_dir: Path, text_list: list[_TextObject],
                       tile_coord: TileCoord, tile_size: int, debug: bool = False):
                if len(component.displayname.strip()) == 0: return
                font = self._type_info._skin.get_font("", self.size+2, assets_dir)
                text_length = int(imd.textlength(component.displayname.replace('\n', ''), font))
                for c1, c2 in internal._with_next(coords):
                    if mathtools.line_in_box(coords, 0, self._type_info._skin.tile_size, 0,
                                             self._type_info._skin.tile_size) and 2 * text_length <= math.dist(c1, c2):
                        # coords[c]
                        #logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Midpoints calculated")
                        t = math.floor(math.dist(c1, c2) / (4 * text_length))
                        t = 1 if t == 0 else t
                        all_points: list[list[tuple[Coord, RealNum]]] \
                            = mathtools.midpoint(c1, c2, self.offset, n=t, return_both=True)
                        for n in range(0, len(all_points), 2):
                            #logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: {component.name}: " +
                            #           f"Generating text {n + 1} of {len(all_points)} in section {coords.index(c1)} of {len(coords) + 1}")
                            p1, p2 = all_points[n][0], all_points[n][1]
                            if self.offset < 0:
                                (tx, ty), trot = p1 if not mathtools.point_in_poly(p1[0].x, p1[0].y,
                                                                                   coords) else p2
                            else:
                                # print(points[0][0], points[0][1], coords)
                                # print(mathtools.point_in_poly(points[0][0], points[0][1], coords))
                                (tx, ty), trot = p1 if mathtools.point_in_poly(p1[0].x, p1[0].y,
                                                                               coords) else p2
                            abt_i = Image.new('RGBA', (2 * text_length, 2 * (self.size + 4)), (0, 0, 0, 0))
                            abt_d = ImageDraw.Draw(abt_i)
                            abt_d.text((text_length, self.size + 4), component.displayname.replace('\n', ''),
                                       fill=self.colour, font=font, anchor="mm",
                                       stroke_width=1, stroke_fill="#dddddd")
                            tw, th = abt_i.size[:]
                            abt_ir = abt_i.rotate(trot, expand=True)
                            abt_ir = abt_ir.crop((0, 0, abt_ir.width, abt_ir.height))
                            text_list.append(_TextObject(abt_ir, tx, ty,
                                                         tw/2, th/2, trot,
                                                         tile_coord, tile_size, imd, debug=debug))

        class AreaCenterText(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "centertext"
                self.colour: str | None = json['colour']
                self.offset: Coord = Coord(*json['offset'])
                self.size: int = json['size']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord], component: Component,
                       assets_dir: Path, text_list: list[_TextObject],
                       tile_coord: TileCoord, tile_size: int, debug: bool = False):
                if len(component.displayname.strip()) == 0: return
                cx, cy = mathtools.poly_center(coords)
                cx += self.offset[0]
                cy += self.offset[1]
                font = self._type_info._skin.get_font("", self.size+2, assets_dir)
                text_length = int(min(imd.textlength(x, font) for x in component.displayname.split('\n')))

                left = min(cl.x for cl in coords)
                right = max(cr.x for cr in coords)
                delta = right - left
                if text_length > delta:
                    #logger.log(f"{style.index(self) + 1}/{len(style)} {component.name}: Breaking up string")
                    tokens = component.displayname.split()
                    wss = re.findall(r"\s+", component.displayname)
                    text = ""
                    for token, ws in list(itertools.zip_longest(tokens, wss, fillvalue='')):
                        temp_text = text[:]
                        temp_text += token
                        if int(imd.textlength(temp_text.split('\n')[-1], font)) > delta:
                            text += '\n' + token + ws
                        else:
                            text += token + ws
                    text_length = int(max(imd.textlength(x, font) for x in text.split("\n")))
                    text_size = int(imd.textsize(text, font)[1] + 4)
                else:
                    text = component.displayname
                    text_size = self.size + 4

                act_i = Image.new('RGBA', (2 * text_length, 2 * text_size), (0, 0, 0, 0))
                act_d = ImageDraw.Draw(act_i)
                act_d.text((text_length, text_size), text, fill=self.colour, font=font, anchor="mm",
                           stroke_width=1, stroke_fill="#dddddd")
                cw, ch = act_i.size[:]
                act_i = act_i.crop((0, 0, act_i.width, act_i.height))
                text_list.append(_TextObject(act_i, cx, cy,
                                             cw/2, ch/2, 0,
                                             tile_coord, tile_size, imd, debug=debug))

        class AreaFill(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self._type_info = type_info
                self.layer = "fill"
                self.colour: str | None = json['colour']
                self.outline: str | None = json['outline']
                self.stripe: tuple[int, int, int] | None = None if json['stripe'] is None else tuple(json['stripe'])
                
            def render(self, imd: ImageDraw.ImageDraw, img: Image.Image, coords: list[Coord], component: Component,
                       nodes: NodeList, tile_coord: TileCoord, size: int, **_):
                ai = Image.new("RGBA", (self._type_info._skin.tile_size, self._type_info._skin.tile_size), (0, 0, 0, 0))
                ad = ImageDraw.Draw(ai)

                if self.stripe is not None:
                    #logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Generating stripes")
                    x_max, x_min, y_max, y_min = tools.line.find_ends(coords)
                    x_max += x_max - x_min
                    x_min -= y_max - y_min
                    y_max += x_max - x_min
                    y_min -= y_max - y_min
                    af_i = Image.new("RGBA", (self._type_info._skin.tile_size, self._type_info._skin.tile_size), (0, 0, 0, 0))
                    af_d = ImageDraw.Draw(af_i)
                    tlx = x_min - 1
                    while tlx <= x_max:
                        af_d.polygon(
                            [(tlx, y_min), (tlx + self.stripe[0], y_min), (tlx + self.stripe[0], y_max),
                             (tlx, y_max)], fill=self.colour)
                        tlx += self.stripe[0] + self.stripe[1]
                    af_i = af_i.rotate(self.stripe[2], center=mathtools.poly_center(coords))
                    mi = Image.new("RGBA", (self._type_info._skin.tile_size, self._type_info._skin.tile_size), (0, 0, 0, 0))
                    md = ImageDraw.Draw(mi)
                    md.polygon(coords, fill=self.colour)
                    pi = Image.new("RGBA", (self._type_info._skin.tile_size, self._type_info._skin.tile_size), (0, 0, 0, 0))
                    pi.paste(af_i, (0, 0), mi)
                    ai.paste(pi, (0, 0), pi)
                else:
                    #logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Filling area")
                    ad.polygon(coords, fill=self.colour, outline=self.outline)

                if component.hollows is not None:
                    for n in component.hollows:
                        n_coords = _node_list_to_image_coords([n], nodes, self._type_info._skin, tile_coord, size)
                        ad.polygon(n_coords, fill=(0, 0, 0, 0))
                img.paste(ai, (0, 0), ai)

                if self.outline is not None:
                    #logger.log(f"{style.index(step) + 1}/{len(style)} {component.name}: Drawing outline")
                    exterior_outline = coords[:]
                    exterior_outline.append(exterior_outline[0])
                    outlines = [exterior_outline]
                    if component.hollows is not None:
                        for n in component.hollows:
                            n_coords = _node_list_to_image_coords([n], nodes, self._type_info._skin, tile_coord, size)
                            n_coords.append(n_coords[0])
                            outlines.append(n_coords)
                    for o_coords in outlines:
                        imd.line(o_coords, fill=self.outline, width=2, joint="curve")

        class AreaCenterImage(ComponentStyle):
            # noinspection PyInitNewSignature
            def __init__(self, json: dict, type_info: Skin.ComponentTypeInfo, *_, **__):
                self.type_info: Skin.ComponentTypeInfo = type_info
                self.layer = "centerimage"
                self.file: Path = Path(json['file'])
                self.offset: Coord = Coord(*json['offset'])
                
            def render(self, img: Image.Image, coords: list[Coord], assets_dir: Path, **_):
                cx, cy = mathtools.poly_center(coords)
                icon = Image.open(assets_dir / self.file)
                img.paste(icon, (cx + self.offset[0], cy + self.offset[1]), icon)
                
    @classmethod
    def from_name(cls, name: str='default') -> Skin:
        """
        Gets a skin from inside the package.

        :param str name: the name of the skin

        :returns: The skin
        :rtype: Skin

        :raises FileNotFoundError: if skin does not exist
        """
        try:
            return cls(internal._read_json(Path(__file__).parent.parent/"skins"/(name+".json")))
        except FileNotFoundError:
            raise FileNotFoundError(f"Skin '{name}' not found")

    @staticmethod
    def validate_json(json: dict) -> Literal[True]:
        """
        Validates a skin JSON file.
    
        :param SkinJson json: the skin JSON file
        
        :returns: Returns True if no errors
        """
        main_schema = Schema({
            "info": {
                "size": int,
                "font": {
                    "": str,
                    "b": str,
                    "i": str,
                    "bi": str
                },
                "background": And(str, Regex(r'^#[a-f,0-9]{3,6}$')),
            },
            "order": [str],
            "types": {
                str: {
                    "tags": list,
                    "type": lambda t_: t_ in ['point', 'line', 'area'],
                    "style": {
                        str: list
                    }
                }
            }
        })
        point_circle = Schema({
            "layer": "circle",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "size": int,
            "width": int
        })
        point_text = Schema({
            "layer": "text",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "offset": And([int], lambda o: len(o) == 2),
            "size": int,
            "anchor": Or(None, str)
        })
        point_square = Schema({
            "layer": "square",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "size": int,
            "width": int
        })
        point_image = Schema({
            "layer": "image",
            "file": str,
            "offset": And([int], lambda o: len(o) == 2)
        })
        line_backfore = Schema({
            "layer": Or("back", "fore"),
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "width": int,
            Optional("dash"): Or(None, And([int], lambda l: len(l) == 2))
        })
        line_text = Schema({
            "layer": "text",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "arrow_colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "size": int,
            "offset": int
        })
        area_fill = Schema({
            "layer": "fill",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            Optional("stripe"): Or(None, And([int], lambda l: len(l) == 3))
        })
        area_bordertext = Schema({
            "layer": "bordertext",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "offset": int,
            "size": int
        })
        area_centertext = Schema({
            "layer": "centertext",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{3,6}$'))),
            "size": int,
            "offset": And(And(list, [int]), lambda o: len(o) == 2)
        })
        area_centerimage = Schema({
            "layer": "image",
            "file": str,
            "offset": And(And(list, [int]), lambda o: len(o) == 2)
        })
    
        schemas = {
            "point": {
                "circle": point_circle,
                "text": point_text,
                "square": point_square,
                "image": point_image
            },
            "line": {
                "text": line_text,
                "back": line_backfore,
                "fore": line_backfore
            },
            "area": {
                "bordertext": area_bordertext,
                "centertext": area_centertext,
                "fill": area_fill,
                "centerimage": area_centerimage
            }
        }
    
        main_schema.validate(json)
        for n, t in json['types'].items():
            if n not in json['order']:
                raise ValueError(f"Type {n} is not in order list")
            s = t['style']
            for z, steps in s.items():
                if internal._str_to_tuple(z)[0] > internal._str_to_tuple(z)[1]:
                    raise ValueError(f"Invalid range '{z}'")
                for step in steps:
                    if not step["layer"] in schemas[t['type']]:
                        raise ValueError(f"Invalid layer '{step}'")
                    else:
                        try:
                            schemas[t['type']][step['layer']].validate(step)
                        except Exception as e:
                            term = blessed.Terminal()
                            print(term.red(f"Type {n}, range {z}, step {step['layer']}"))
                            raise e
        return True