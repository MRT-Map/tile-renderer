from dataclasses import dataclass
from pathlib import Path

from ..skin_type import Skin
from .zoom_params import ZoomParams


@dataclass(frozen=True, init=True, unsafe_hash=True)
class Config:
    """
    The configuration for the render job.
    """

    zoom: ZoomParams
    """A ZoomParams object"""
    export_id: str = "unnamed"
    """The skin to use for rendering the tiles"""
    temp_dir: Path = Path.cwd() / "temp"
    """The temporary data folder that will be used to save data"""
    skin: Skin = Skin.from_name("default")
    """The skin to use for rendering the tiles"""
    assets_dir: Path = Path(__file__).parent.parent / "skins" / "assets"
    """The asset directory for the skin"""
