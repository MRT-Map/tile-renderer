from dataclasses import dataclass
from pathlib import Path

from ..skin_type import Skin
from .zoom_params import ZoomParams


@dataclass(frozen=True, init=True, unsafe_hash=True)
class Config:
    """
    The configuration for the render job.
    :param ZoomParams zoom: A ZoomParams object
    :param Skin skin: The skin to use for rendering the tiles
    :param str export_id: The name of the rendering task
    :param Path assets_dir: The asset directory for the skin
    :param Path temp_dir: the temporary data folder that will be used to save data
    """

    zoom: ZoomParams
    export_id: str = "unnamed"
    temp_dir: Path = Path.cwd() / "temp"
    skin: Skin = Skin.from_name("default")
    assets_dir: Path = Path(__file__).parent.parent / "skins" / "assets"
