import tempfile
from pathlib import Path

import requests

from tile_renderer.types.colour import Colour
from tile_renderer.types.skin import AreaCentreText, AreaFill, ComponentType, LineBack, LineFore, LineText, Skin


def get_url(url: str) -> bytes:
    path = Path(tempfile.gettempdir()) / "tile-renderer" / "url" / url
    if path.exists():
        return path.read_bytes()
    response = requests.get(url).content  # noqa: S113
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    path.write_bytes(response)
    return response


WATER = Colour.from_hex(0x87CEEB)
LAND = Colour.from_hex(0xDDDDDD)
A_ROAD = Colour.from_hex(0xFFAAAA)
B_ROAD = Colour.from_hex(0xFF8000)
LOCAL_HIGHWAY = Colour.from_hex(0xFFCC80)
LOCAL_MAIN = Colour.from_hex(0xFFEE00)
LOCAL_SECONDARY = Colour.from_hex(0xFFF899)
LOCAL_TERTIARY_QUATERNARY = Colour.from_hex(0xEEEEEE)
LOCAL_PEDESTRIAN = Colour.from_hex(0xCCCCFF)
BUILDING = Colour.from_hex(0xA2A288)
TRANSPORT_BUILDING = Colour.from_hex(0x999966)


# noinspection PyListCreation
def main():
    types: list[ComponentType] = []

    types.append(
        ComponentType(
            name="waterLarge",
            shape="area",
            styles={"0-": [AreaFill(colour=WATER), AreaCentreText(colour=WATER.darkened(), size=10.0)]},
        )
    )
    types.append(
        ComponentType(
            name="waterSmall",
            shape="area",
            styles={
                "0-2": [AreaFill(colour=WATER), AreaCentreText(colour=WATER.darkened(), size=5.0)],
                "3-6": [
                    AreaFill(colour=WATER),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="landLarge",
            shape="area",
            styles={
                "0-5": [AreaFill(colour=LAND), AreaCentreText(colour=LAND.darkened(), size=10.0)],
                "6-": [
                    AreaFill(colour=LAND),
                ],
            },
        )
    )
    types.append(
        ComponentType(
            name="landSmall",
            shape="area",
            styles={
                "0-2": [AreaFill(colour=LAND), AreaCentreText(colour=LAND.darkened(), size=5.0)],
                "3-": [
                    AreaFill(colour=LAND),
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
                    LineFore(colour=WATER, width=2.0),
                    LineText(colour=WATER.darkened(), arrow_colour=WATER.darkened(), size=4.0),
                ],
                "3-4": [
                    LineFore(colour=WATER, width=0.6),
                ],
            },
        )
    )

    for name, colour in (
        ("grass", 0xBBFF99),
        ("shrub", 0x99FF99),
        ("forest", 0x5CA904),
        ("stone", 0xAAAAAA),
        ("sand", 0xF7E1A1),
        ("residentialArea", 0xB3CBCB),
        ("industrialArea", 0xFFCCB3),
        ("commercialArea", 0xE7B1CA),
        ("officeArea", 0xFFCC99),
        ("residentialOfficeArea", 0xD9DBB2),
        ("schoolArea", 0xECC6C6),
        ("healthArea", 0xFF9999),
        ("agricultureArea", 0xCCFF99),
        ("militaryArea", 0xC2C2A3),
    ):
        colour = Colour.from_hex(colour)
        types.append(
            ComponentType(
                name=name,
                shape="area",
                styles={
                    "0-3": [
                        AreaFill(colour=colour, outline=colour.darkened(20.0), outline_width=0.5),
                        AreaCentreText(colour=colour.darkened(20.0), size=5.0),
                    ],
                    "4-6": [AreaFill(colour=colour, outline=colour.darkened(20.0), outline_width=0.5 / 1.5**4)],
                },
            )
        )

    types.append(
        ComponentType(
            name="gate",
            shape="area",
            styles={
                "0-2": [
                    AreaFill(colour=Colour.from_hex(0x33334D)),
                    AreaCentreText(colour=Colour.from_hex(0x33334D).darkened(), size=2.0),
                ],
                "3-5": [
                    AreaFill(colour=Colour.from_hex(0x33334D)),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="apron",
            shape="area",
            styles={
                "0-5": [
                    AreaFill(colour=Colour.from_hex(0xC2C2D6)),
                    AreaCentreText(colour=Colour.from_hex(0xC2C2D6).darkened(), size=3.0),
                ]
            },
        )
    )

    types.append(
        ComponentType(
            name="taxiway",
            shape="line",
            styles={
                "0-2": [
                    LineFore(colour=Colour.from_hex(0x8F8FA3), width=10.0, zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x8F8FA3).darkened(),
                        arrow_colour=Colour.from_hex(0x8F8FA3).darkened(),
                        size=4.0,
                    ),
                ],
                "3-5": [
                    LineFore(colour=Colour.from_hex(0x8F8FA3), width=10.0, zoom_multiplier=2.0),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="runway",
            shape="line",
            styles={
                "0-1": [
                    LineFore(colour=Colour.from_hex(0x73738C), width=20.0, unrounded=True, zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x73738C).darkened(),
                        arrow_colour=Colour.from_hex(0x73738C).darkened(),
                        size=4.0,
                    ),
                ],
                "2-5": [
                    LineFore(colour=Colour.from_hex(0x73738C), width=20.0 / 2**2, unrounded=True, zoom_multiplier=2.0),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="wideRunway",
            shape="line",
            styles={
                "0-1": [
                    LineFore(colour=Colour.from_hex(0x73738C), width=40.0, unrounded=True, zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x73738C).darkened(),
                        arrow_colour=Colour.from_hex(0x73738C).darkened(),
                        size=8.0,
                    ),
                ],
                "2-5": [
                    LineFore(colour=Colour.from_hex(0x73738C), width=40.0 / 2**2, unrounded=True, zoom_multiplier=2.0),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="helipad",
            shape="area",
            styles={
                "0-1": [
                    AreaFill(
                        colour=Colour.from_hex(0xFF99FF),
                        outline=Colour.from_hex(0xFF99FF).darkened(),
                        outline_width=0.5,
                    ),
                    AreaCentreText(colour=Colour.from_hex(0xFF99FF).darkened(), size=2.0),
                ]
            },
        )
    )

    types.append(
        ComponentType(
            name="plaza",
            shape="area",
            styles={
                "0-2": [
                    AreaFill(
                        colour=Colour.from_hex(0xCCCCFF),
                        outline=Colour.from_hex(0xCCCCFF).darkened(),
                        outline_width=0.5,
                    ),
                    AreaCentreText(colour=Colour.from_hex(0xCCCCFF).darkened(), size=3.0),
                ],
                "3-6": [
                    AreaFill(
                        colour=Colour.from_hex(0xCCCCFF),
                        outline=Colour.from_hex(0xCCCCFF).darkened(),
                        outline_width=0.5 / 1.5**3,
                    ),
                ],
            },
        )
    )

    for name, col in (
        ("building_underground", BUILDING),
        ("cityHall_underground", Colour.from_hex(0xFFAAAA)),
        ("transportBuilding_underground", TRANSPORT_BUILDING),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="area",
                styles={
                    "0-2": [
                        AreaFill(colour=col.brightened(), outline=col, outline_width=0.5),
                        AreaCentreText(colour=col.darkened(), size=3.0),
                    ],
                    "3-5": [
                        AreaFill(colour=col.brightened(), outline=col, outline_width=0.5 / 1.5**3),
                    ],
                },
            )
        )

    types.append(
        ComponentType(
            name="park",
            shape="area",
            styles={
                "0-2": [
                    AreaFill(
                        colour=Colour.from_hex(0x669900),
                        outline=Colour.from_hex(0x669900).darkened(20.0),
                        outline_width=0.5,
                    ),
                    AreaCentreText(colour=Colour.from_hex(0x669900).darkened(20.0), size=4.0),
                ],
                "3-6": [
                    AreaFill(
                        colour=Colour.from_hex(0x669900),
                        outline=Colour.from_hex(0x669900).darkened(20.0),
                        outline_width=0.5 / 1.5**3,
                    ),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="pathway_underground",
            shape="line",
            tags=["road"],
            styles={
                "0-4": [
                    LineBack(colour=Colour.from_hex(0xEEEEEE), width=1.5, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0x66FF66), width=0.8, dash=[3.2, 3.2], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0xAAAAAA),
                        arrow_colour=Colour.from_hex(0xEEEEEE),
                        size=3.2,
                        offset=2.0,
                        zoom_multiplier=2.0,
                    ),
                ]
            },
        )
    )

    for name, col, width, small_width in (
        ("localHighwaySlip_underground", LOCAL_HIGHWAY, 4.0, 0.1),
        ("bRoadSlip_underground", B_ROAD, 4.8, 0.2),
        ("aRoadSlip_underground", A_ROAD, 6.4, 0.3),
        ("localPedestrianQuaternaryRoad_underground", LOCAL_PEDESTRIAN, 3.2, 0.1),
        ("localQuaternaryRoad_underground", LOCAL_TERTIARY_QUATERNARY, 3.2, 0.1),
        ("localPedestrianTertiaryRoad_underground", LOCAL_PEDESTRIAN, 4.8, 0.2),
        ("localTertiaryRoad_underground", LOCAL_TERTIARY_QUATERNARY, 4.8, 0.2),
        ("localSecondaryRoad_underground", LOCAL_SECONDARY, 5.6, 0.2),
        ("localMainRoad_underground", LOCAL_MAIN, 6.4, 0.3),
        ("localHighway_underground", LOCAL_HIGHWAY, 7.2, 0.3),
        ("bRoad_underground", B_ROAD, 8.0, 0.4),
        ("aRoad_underground", A_ROAD, 9.6, 0.4),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(colour=col, width=width + 1.6, zoom_multiplier=2),
                        LineFore(colour=col.brightened(), width=width, zoom_multiplier=2),
                        LineText(colour=Colour.from_hex(0x000000), arrow_colour=col, size=width, zoom_multiplier=2),
                    ],
                    "5-8": [
                        LineBack(colour=col, width=small_width * 1.5),
                        LineFore(colour=col.brightened(), width=small_width),
                    ],
                },
            )
        )

    types.append(
        ComponentType(
            name="rail_underground",
            shape="line",
            tags=["road"],
            styles={
                "0-2": [
                    LineFore(colour=Colour.from_hex(0x808080), width=1.5, dash=[10.0, 5.0]),
                    LineText(
                        colour=Colour.from_hex(0x808080), arrow_colour=Colour.from_hex(0x808080), offset=3.2, size=3.2
                    ),
                ],
                "3-4": [LineFore(colour=Colour.from_hex(0x808080), width=0.5, dash=[4.0, 2.0])],
            },
        )
    )

    types.append(
        ComponentType(
            name="intercityRail_underground",
            shape="line",
            tags=["road"],
            styles={
                "0-2": [
                    LineFore(colour=Colour.from_hex(0x808080), width=3.2, dash=[10.0, 5.0], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x808080),
                        arrow_colour=Colour.from_hex(0x808080),
                        offset=3.2,
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [LineFore(colour=Colour.from_hex(0x808080), width=0.4, dash=[4.0, 2.0], zoom_multiplier=2.0)],
            },
        )
    )

    types.append(
        ComponentType(
            name="platform_underground",
            shape="area",
            styles={
                "0-1": [
                    AreaFill(
                        colour=Colour.from_hex(0xAAAAAA),
                        outline=Colour.from_hex(0xAAAAAA).darkened(),
                        outline_width=0.5,
                    ),
                    AreaCentreText(colour=Colour.from_hex(0xAAAAAA).darkened(), size=2.0),
                ],
                "2-3": [
                    AreaFill(
                        colour=Colour.from_hex(0xAAAAAA),
                        outline=Colour.from_hex(0xAAAAAA).darkened(),
                        outline_width=0.5,
                    ),
                ],
            },
        )
    )

    for name, col in (
        ("building", BUILDING),
        ("cityHall", Colour.from_hex(0xFFAAAA)),
        ("transportBuilding", TRANSPORT_BUILDING),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="area",
                styles={
                    "0-2": [
                        AreaFill(colour=col, outline=col.darkened(), outline_width=0.5),
                        AreaCentreText(colour=col.darkened(), size=3.0),
                    ],
                    "3-5": [
                        AreaFill(colour=col, outline=col.darkened(), outline_width=0.5 / 1.5**3),
                    ],
                },
            )
        )

    types.append(
        ComponentType(
            name="pathway",
            shape="line",
            tags=["road"],
            styles={
                "0-4": [
                    LineBack(colour=Colour.from_hex(0xEEEEEE), width=1.5, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0x008000), width=0.8, dash=[3.2, 3.2], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0xAAAAAA),
                        arrow_colour=Colour.from_hex(0xEEEEEE),
                        size=3.2,
                        offset=2.0,
                        zoom_multiplier=2.0,
                    ),
                ]
            },
        )
    )

    for name, col, width, small_width in (
        ("localHighwaySlip", LOCAL_HIGHWAY, 4.0, 0.1),
        ("bRoadSlip", B_ROAD, 4.8, 0.2),
        ("aRoadSlip", A_ROAD, 6.4, 0.3),
        ("localPedestrianQuaternaryRoad", LOCAL_PEDESTRIAN, 3.2, 0.1),
        ("localQuaternaryRoad", LOCAL_TERTIARY_QUATERNARY, 3.2, 0.1),
        ("localPedestrianTertiaryRoad", LOCAL_PEDESTRIAN, 4.8, 0.2),
        ("localTertiaryRoad", LOCAL_TERTIARY_QUATERNARY, 4.8, 0.2),
        ("localSecondaryRoad", LOCAL_SECONDARY, 5.6, 0.2),
        ("localMainRoad", LOCAL_MAIN, 6.4, 0.3),
        ("localHighway", LOCAL_HIGHWAY, 3.6, 0.3),
        ("bRoad", B_ROAD, 8.0, 0.4),
        ("aRoad", A_ROAD, 9.6, 0.4),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(colour=col.darkened(), width=width + 1.6, zoom_multiplier=2),
                        LineFore(colour=col, width=width, zoom_multiplier=2),
                        LineText(colour=Colour.from_hex(0x000000), arrow_colour=col, size=width, zoom_multiplier=2),
                    ],
                    "5-8": [
                        LineBack(colour=col.darkened(), width=small_width * 1.5),
                        LineFore(colour=col, width=small_width),
                    ],
                },
            )
        )

    types.append(
        ComponentType(
            name="rail",
            shape="line",
            tags=["road"],
            styles={
                "0-2": [
                    LineFore(colour=Colour.from_hex(0x808080), width=1.5, zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x808080),
                        arrow_colour=Colour.from_hex(0x808080),
                        offset=3.2,
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-4": [LineFore(colour=Colour.from_hex(0x808080), width=0.5, zoom_multiplier=2.0)],
            },
        )
    )

    types.append(
        ComponentType(
            name="intercityRail",
            shape="line",
            tags=["road"],
            styles={
                "0-2": [
                    LineBack(colour=Colour.from_hex(0x808080), width=3.2, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=1.5, dash=[10.0, 10.0], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x808080),
                        arrow_colour=Colour.from_hex(0x808080),
                        offset=3.2,
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [
                    LineBack(colour=Colour.from_hex(0x808080), width=0.8),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=0.4, dash=[4.0, 4.0]),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="pathway_elevated",
            shape="line",
            tags=["road"],
            styles={
                "0-4": [
                    LineBack(colour=Colour.from_hex(0x333333), width=2.4, zoom_multiplier=2.0),
                    LineBack(colour=Colour.from_hex(0xEEEEEE), width=1.5, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0x008000), width=0.8, dash=[3.2, 3.2], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0xAAAAAA),
                        arrow_colour=Colour.from_hex(0xEEEEEE),
                        size=3.2,
                        offset=2.0,
                        zoom_multiplier=2.0,
                    ),
                ]
            },
        )
    )

    for name, col, width, small_width in (
        ("localHighwaySlip_elevated", LOCAL_HIGHWAY, 4.0, 0.1),
        ("bRoadSlip_elevated", B_ROAD, 4.8, 0.2),
        ("aRoadSlip_elevated", A_ROAD, 6.4, 0.3),
        ("localPedestrianQuaternaryRoad_elevated", LOCAL_PEDESTRIAN, 3.2, 0.1),
        ("localQuaternaryRoad_elevated", LOCAL_TERTIARY_QUATERNARY, 3.2, 0.1),
        ("localPedestrianTertiaryRoad_elevated", LOCAL_PEDESTRIAN, 4.8, 0.2),
        ("localTertiaryRoad_elevated", LOCAL_TERTIARY_QUATERNARY, 4.8, 0.2),
        ("localSecondaryRoad_elevated", LOCAL_SECONDARY, 5.6, 0.2),
        ("localMainRoad_elevated", LOCAL_MAIN, 6.4, 0.3),
        ("localHighway_elevated", LOCAL_HIGHWAY, 7.2, 0.3),
        ("bRoad_elevated", B_ROAD, 8.0, 0.4),
        ("aRoad_elevated", A_ROAD, 9.6, 0.4),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(colour=Colour.from_hex(0x333333), width=width + 1.6, zoom_multiplier=2),
                        LineFore(colour=col, width=width, zoom_multiplier=2),
                        LineText(colour=Colour.from_hex(0x000000), arrow_colour=col, size=width, zoom_multiplier=2),
                    ],
                    "5-8": [
                        LineBack(colour=Colour.from_hex(0x333333), width=small_width * 1.5),
                        LineFore(colour=col, width=small_width),
                    ],
                },
            )
        )

    types.append(
        ComponentType(
            name="rail_elevated",
            shape="line",
            tags=["road"],
            styles={
                "0-2": [
                    LineBack(colour=Colour.from_hex(0x333333), width=2.4, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0x808080), width=1.5, zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x808080),
                        arrow_colour=Colour.from_hex(0x808080),
                        offset=3.2,
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-4": [
                    LineBack(colour=Colour.from_hex(0x333333), width=0.8),
                    LineFore(colour=Colour.from_hex(0x808080), width=0.5),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="intercityRail_elevated",
            shape="line",
            tags=["road"],
            styles={
                "0-2": [
                    LineBack(colour=Colour.from_hex(0x333333), width=4.0, zoom_multiplier=2.0),
                    LineBack(colour=Colour.from_hex(0x808080), width=3.2, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=1.5, dash=[10.0, 10.0], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x808080),
                        arrow_colour=Colour.from_hex(0x808080),
                        offset=3.2,
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [
                    LineBack(colour=Colour.from_hex(0x333333), width=1.2),
                    LineBack(colour=Colour.from_hex(0x808080), width=0.8),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=0.5, dash=[4.0, 4.0]),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="platform",
            shape="area",
            styles={
                "0-1": [
                    AreaFill(colour=Colour.from_hex(0xCCCCCC), outline=Colour.from_hex(0x808080), outline_width=0.5),
                    AreaCentreText(colour=Colour.from_hex(0x808080), size=2.0),
                ],
                "2-3": [
                    AreaFill(colour=Colour.from_hex(0xCCCCCC), outline=Colour.from_hex(0x808080), outline_width=0.5),
                ],
            },
        )
    )

    skin = Skin(
        name="default",
        font_files=[
            get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Regular.ttf"
            ),
            get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Bold.ttf"
            ),
            get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Italic.ttf"
            ),
            get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-BoldItalic.ttf"
            ),
            get_url("https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/NotoSansCJKjp-VF.ttf"),
            # get_url(
            #     "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/NotoSansCJKsc-VF.ttf"
            # ),
            # get_url(
            #     "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/NotoSansCJKtc-VF.ttf"
            # ),
            # get_url(
            #     "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/NotoSansCJKhk-VF.ttf"
            # ),
            # get_url(
            #     "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/NotoSansCJKkr-VF.ttf"
            # )
        ],
        font_string="'Noto Sans', 'Noto Sans JP'",
        background=LAND,
        types=types,
        prune_small_text=0.5,
        licence=(Path(__file__).parent / "default_licences.md").read_text(),
    )
    skin.save_json(Path(__file__).parent)


if __name__ == "__main__":
    main()
