import os

import renderer.internal as internal
import renderer.tools as tools
import renderer.validate as validate
import renderer.mathtools as mathtools
import renderer.rendering as rendering

def getSkin(name: str):
    """
    Gets the skin JSON, given the name.
    More info: https://tile-renderer.readthedocs.io/en/main/functions.html#renderer.misc.getSkin
    """
    try:
        return internal.readJson(os.path.dirname(__file__)+"/skins/"+name+".json")
    except FileNotFoundError:
        raise FileNotFoundError(f"Skin '{name}' not found")