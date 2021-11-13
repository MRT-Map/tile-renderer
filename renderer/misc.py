import os

import renderer.internals.internal as internal
from renderer.types import *

def get_skin(name: str= 'default') -> SkinJson:
    """
    Gets the skin JSON, given the name.
    More info: https://tile-renderer.readthedocs.io/en/latest/functions.html#renderer.misc.getSkin
    """
    try:
        return internal._read_json(os.path.dirname(__file__) + "/skins/" + name + ".json")
    except FileNotFoundError:
        raise FileNotFoundError(f"Skin '{name}' not found")