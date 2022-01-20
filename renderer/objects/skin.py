from __future__ import annotations
from typing import Literal, Dict, Tuple, List, Union
from pathlib import Path

import blessed
from PIL import ImageFont, ImageDraw
from schema import Schema, And, Or, Regex, Optional

import renderer.internals.internal as internal
from renderer.types import RealNum, SkinJson, SkinType, Coord


class Skin:
    """Represents a skin.

    :param SkinJson json: The JSON of the skin."""
    def __init__(self, json: SkinJson):
        self.validate_json(json)
        self.tile_size: int = json['info']['size']
        self.fonts: Dict[str, Path] = {name: Path(path) for name, path in json['info']['font'].items()}
        self.background: str = json['info']['background']

        self.order: List[str] = json['order']
        self.types: Dict[str, Skin.ComponentTypeInfo] \
            = {name: self.ComponentTypeInfo(name, value, self.order) for name, value in json['types'].items()}

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
        :param List[str] order: Will set ``_order``"""
        def __init__(self, name: str, json: SkinType, order: List[str]):
            self.name: str = name
            """The name of the component."""
            self.tags: List[str] = json['tags']
            """The list of tags attributed to the component."""
            self.shape: Literal["point", "line", "area"] = json['type']
            """The shape of the component, must be one of ``point``, ``line``, ``area``"""
            self._order = order
            self.styles: Dict[Tuple[int, int], List[Skin.ComponentTypeInfo.ComponentStyle]] \
                = {internal._str_to_tuple(range_): [self.ComponentStyle(v) for v in value] for range_, value in json['style'].items()}
            """The styles of the object, denoted as ``{(max_zoom, min_zoom): [style, ...]}``"""

        def __getitem__(self, zoom_level: int) -> List[ComponentStyle]:
            for (max_level, min_level), styles in self.styles.items():
                if max_level <= zoom_level <= min_level:
                    return styles
            else:
                return []
        
        class ComponentStyle:
            """Represents the ``styles`` portion of a ComponentTypeInfo.

            :param dict json: The JSON of the styles"""
            def __new__(cls, json: dict, shape: Literal["point", "line", "area"]):
                if cls != Skin.ComponentTypeInfo.ComponentStyle: super().__new__(cls)
                if shape == "point":
                    if json['layer'] == "circle": return Skin.ComponentTypeInfo.PointCircle(Skin.ComponentTypeInfo.PointCircle, json)
                    if json['layer'] == "text": return Skin.ComponentTypeInfo.PointText(Skin.ComponentTypeInfo.PointText, json)
                    if json['layer'] == "square": return Skin.ComponentTypeInfo.PointSquare(Skin.ComponentTypeInfo.PointSquare, json)
                    if json['layer'] == "image": return Skin.ComponentTypeInfo.PointImage(Skin.ComponentTypeInfo.PointImage, json)
                elif shape == "line":
                    if json['layer'] == "text": return Skin.ComponentTypeInfo.LineText(Skin.ComponentTypeInfo.LineText, json)
                    if json['layer'] == "back": return Skin.ComponentTypeInfo.LineBack(Skin.ComponentTypeInfo.LineBack, json)
                    if json['layer'] == "fore": return Skin.ComponentTypeInfo.LineFore(Skin.ComponentTypeInfo.LineFore, json)
                elif shape == "area":
                    if json['layer'] == "bordertext": return Skin.ComponentTypeInfo.AreaBorderText(Skin.ComponentTypeInfo.AreaBorderText, json)
                    if json['layer'] == "centertext": return Skin.ComponentTypeInfo.AreaCenterText(Skin.ComponentTypeInfo.AreaCenterText, json)
                    if json['layer'] == "fill": return Skin.ComponentTypeInfo.AreaFill(Skin.ComponentTypeInfo.AreaFill, json)
                    if json['layer'] == "centerimage": return Skin.ComponentTypeInfo.AreaCenterImage(Skin.ComponentTypeInfo.AreaCenterImage, json)
                raise ValueError(f"No layer in shape")
            
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]): pass

        class PointCircle(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.outline: str | None = json['outline']
                self.size: int = json['size']
                self.width: int = json['width']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
                imd.ellipse((coords[0].x - self.size / 2 + 1,
                             coords[0].y - self.size / 2 + 1,
                             coords[0].x + self.size / 2,
                             coords[0].y + self.size / 2),
                            fill=self.colour, outline=self.outline, width=self.width)


        class PointText(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.size: int = json['size']
                self.offset: Coord = Coord(*json['offset'])
                self.anchor: str = json['anchor']
                
            def render(self, imd: ImageDraw, coords: list[Coord], 
                       displayname: str, skin: Skin, assets_dir: Path, points_text_list: list[_TextObject]):
                font = skin.get_font("", self.size, assets_dir)
                text_length = int(imd.textlength(displayname, font))
                pt_i = Image.new('RGBA', (2 * text_length, 2 * (self.size + 4)), (0, 0, 0, 0))
                pt_d = ImageDraw.Draw(pt_i)
                pt_d.text((text_length, self.size + 4), displayname, fill=self.colour, font=font,
                          anchor="mm")
                tw, th = pt_i.size
                points_text_list.append(_TextObject(pt_i, coords[0].x + self.offset[0], coords[0].y + self.offset[1], tw, th, 0))
                #font = skin.get_font("", step.size)
                #img.text((coords[0][0]+step.offset[0], coords[0][1]+step.offset[1]), component.displayname, fill=step.colour, font=font, anchor=step['anchor'])

            
        class PointSquare(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.outline: str | None = json['outline']
                self.size: int = json['size']
                self.width: int = json['width']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
                imd.rectangle((coords[0].x - self.size / 2 + 1,
                               coords[0].y - self.size / 2 + 1,
                               coords[0].x + self.size / 2,
                               coords[0].y + self.size / 2),
                              fill=self.colour, outline=self.outline, width=self.width)


        class PointImage(ComponentStyle):
            def __init__(self, json: dict):
                self.file: Path = Path(json['file'])
                self.offset: Coord = Coord(*json['offset'])
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord],
                       assets_dir: Path):
                icon = Image.open(assets_dir/self.file)
                img.paste(icon, (int(coords[0].x - icon.width / 2 + self.offset[0]),
                                 int(coords[0].y - icon.height / 2 + self.offset[1])), icon)


        class LineText(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.size: int = json['size']
                self.offset: int = json['offset']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
               
        class LineBack(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.width: int = json['width']
                self.dash: tuple[int, int] = json['dash']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
                
        LineFront = LineBack

        class AreaBorderText(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.offset: int = json['offset']
                self.size: int = json['size']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
                

        class AreaCenterText(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.offset: Coord = Coord(*json['offset'])
                self.size: int = json['size']
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
                

        class AreaFill(ComponentStyle):
            def __init__(self, json: dict):
                self.colour: str | None = json['colour']
                self.outline: str | None = json['outline']
                self.stripe: tuple[int, int, int] = tuple(json['stripe'])
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
                

        class AreaCenterImage(ComponentStyle):
            def __init__(self, json: dict):
                self.file: Path = Path(json['file'])
                self.offset: Coord = Coord(*json['offset'])
                
            def render(self, imd: ImageDraw.ImageDraw, coords: list[Coord]):
                

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
        mainSchema = Schema({
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
    
        mainSchema.validate(json)
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