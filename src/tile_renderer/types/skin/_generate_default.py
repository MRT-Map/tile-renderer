import tempfile
from pathlib import Path

import requests

from tile_renderer.types.colour import Colour
from tile_renderer.types.skin import AreaCentreText, AreaFill, ComponentType, LineFore, LineText, Skin


def get_url(url: str) -> bytes:
    path = Path(tempfile.gettempdir()) / "renderer" / "url" / url
    if path.exists():
        return path.read_bytes()
    response = requests.get(url).content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    path.write_bytes(response)
    return response


# noinspection PyListCreation
def main():
    WATER_COL = Colour.from_hex(0x87CEEB)
    LAND_COL = Colour.from_hex(0xDDDDDD)
    types: list[ComponentType] = []

    types.append(
        ComponentType(
            name="waterLarge",
            shape="area",
            styles={"0-": [AreaFill(colour=WATER_COL), AreaCentreText(colour=WATER_COL.darkened(), size=50)]},
        )
    )
    types.append(
        ComponentType(
            name="waterSmall",
            shape="area",
            styles={
                "0-2": [AreaFill(colour=WATER_COL), AreaCentreText(colour=WATER_COL.darkened(), size=25)],
                "3-": [
                    AreaFill(colour=WATER_COL),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="landLarge",
            shape="area",
            styles={
                "0-5": [AreaFill(colour=LAND_COL), AreaCentreText(colour=LAND_COL.darkened(), size=50)],
                "6-": [
                    AreaFill(colour=LAND_COL),
                ],
            },
        )
    )
    types.append(
        ComponentType(
            name="landSmall",
            shape="area",
            styles={
                "0-2": [AreaFill(colour=LAND_COL), AreaCentreText(colour=LAND_COL.darkened(), size=25)],
                "3-": [
                    AreaFill(colour=LAND_COL),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="waterway",
            shape="line",
            styles={
                "0-2": [
                    LineFore(colour=WATER_COL, width=10),
                    LineText(colour=WATER_COL.darkened(), arrow_colour=WATER_COL.darkened(), size=20),
                ],
                "3-4": [
                    LineFore(colour=WATER_COL, width=3),
                ],
            },
        )
    )

    skin = Skin(
        name="default",
        fonts={
            "": get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Regular.ttf"
            ),
            "b": get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Bold.ttf"
            ),
            "i": get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Italic.ttf"
            ),
            "bi": get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-BoldItalic.ttf"
            ),
        },
        background=LAND_COL,
        types=types,
        licence=(Path(__file__).parent / "default_licences.md").read_text(),
    )
    skin.save_json(Path(__file__).parent)


if __name__ == "__main__":
    main()
