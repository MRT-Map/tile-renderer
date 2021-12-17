from __future__ import annotations
from typing import Literal, Dict, Tuple, List
from pathlib import Path

from schema import Schema, And, Or, Regex, Optional

import renderer.internals.internal as internal

class Skin:
    def __init__(self, json: dict):
        self.validate_json(json)
        self.tile_size: int = json['info']['size']
        self.fonts: Dict[str, Path] = {name: Path(path) for name, path in json['info']['fonts'].items()}
        self.background: Tuple[int, int, int] = json['info']['background']

        self.order: List[str] = json['order']
        self.types: Dict[str, Skin.ComponentTypeInfo] \
            = {name: self.ComponentTypeInfo(name, value, self.order) for name, value in json['types'].items()}

    def __getitem__(type_name: str) -> Skin.ComponentTypeInfo:
        return self.types[type_name]
    
    class ComponentTypeInfo:
        def __init__(self, name: str, json: dict, order: List[str]):
            self.name: str = name
            self.tags: List[str] = json['tags']
            self.shape = json['type']
            self.styles: Dict[Tuple[int, int], List[Skin.ComponentTypeInfo.ComponentStyle]] \
                = {internal._str_to_tuple(range_): [self.ComponentStyle(v) for v in value] for range_, value in json['styles'].items()}

        def __getitem__(zoom: int) -> Skin.ComponentTypeInfo.ComponentStyle:
            pass
        
        class ComponentStyle:
            def __init__(self, json: dict):
                self.layer: str = json['layer']
                self.colour: str = None if "colour" not in json else json['colour']
                self.outline: str = None if "outline" not in json else json['outline']
                self.offset: Union[RealNum, Tuple[RealNum, RealNum]] = None if "offset" not in json else tuple(json['offset']) if issubclass(json['offset'], list) else json['offset']
                self.size: int = None if "size" not in json else json['size']
                self.anchor: str = None if "anchor" not in json else json['anchor']
                self.file: Path = None if "file" not in json else Path(json['file'])
                self.width: int = None if "width" not in json else json['width']
    
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
                "background": And([int], lambda l: len(l) == 3 and False not in [0 <= n_ <= 255 for n_ in l])
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
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "size": int,
            "width": int
        })
        point_text = Schema({
            "layer": "text",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "offset": And([int], lambda o: len(o) == 2),
            "size": int,
            "anchor": Or(None, str)
        })
        point_square = Schema({
            "layer": "square",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
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
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "width": int,
            Optional("dash"): And([int], lambda l: len(l) == 2)
        })
        line_text = Schema({
            "layer": "text",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "size": int,
            "offset": int
        })
        area_fill = Schema({
            "layer": "fill",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "outline": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            Optional("stripe"): And([int], lambda l: len(l) == 3)
        })
        area_bordertext = Schema({
            "layer": "bordertext",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
            "offset": int,
            "size": int
        })
        area_centertext = Schema({
            "layer": "centertext",
            "colour": Or(None, And(str, Regex(r'^#[a-f,0-9]{6}$'))),
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
    
        mainSchema.validate(skin_json)
        for n, t in skin_json['types'].items():
            if n not in skin_json['order']:
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