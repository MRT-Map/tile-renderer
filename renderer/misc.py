import os

import renderer.internals.internal as internal
from renderer.types import *

def get_skin(name: str= 'default') -> SkinJson:
    """
    Gets a skin from inside the package.

    :param str name: the name of the skin
    
    :returns: The skin JSON
    :rtype: dict

    :raises FileNotFoundError: if skin does not exist
    """
    try:
        return internal._read_json(os.path.dirname(__file__) + "/skins/" + name + ".json")
    except FileNotFoundError:
        raise FileNotFoundError(f"Skin '{name}' not found")