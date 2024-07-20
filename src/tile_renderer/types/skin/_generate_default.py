import tempfile
from pathlib import Path

import requests

from tile_renderer.types.colour import Colour
from tile_renderer.types.skin import AreaCentreText, AreaFill, ComponentType, LineFore, LineText, Skin, LineBack


def get_url(url: str) -> bytes:
    path = Path(tempfile.gettempdir()) / "renderer" / "url" / url
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
            styles={"0-": [AreaFill(colour=WATER), AreaCentreText(colour=WATER.darkened(), size=50)]},
        )
    )
    types.append(
        ComponentType(
            name="waterSmall",
            shape="area",
            styles={
                "0-2": [AreaFill(colour=WATER), AreaCentreText(colour=WATER.darkened(), size=25)],
                "3-": [
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
                "0-5": [AreaFill(colour=LAND), AreaCentreText(colour=LAND.darkened(), size=50)],
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
                "0-2": [AreaFill(colour=LAND), AreaCentreText(colour=LAND.darkened(), size=25)],
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
                    LineFore(colour=WATER, width=10),
                    LineText(colour=WATER.darkened(), arrow_colour=WATER.darkened(), size=20),
                ],
                "3-4": [
                    LineFore(colour=WATER, width=3),
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
                        AreaFill(colour=colour, outline=colour.darkened()),
                        AreaCentreText(colour=colour.darkened(), size=25),
                    ],
                    "4-6": [AreaFill(colour=colour, outline=colour.darkened())],
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
                    AreaCentreText(colour=Colour.from_hex(0x33334D).darkened(), size=10),
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
                    AreaCentreText(colour=Colour.from_hex(0xC2C2D6).darkened(), size=15),
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
                    LineFore(colour=Colour.from_hex(0x8F8FA3), width=50),
                    LineText(
                        colour=Colour.from_hex(0x8F8FA3).darkened(),
                        arrow_colour=Colour.from_hex(0x8F8FA3).darkened(),
                        size=20,
                    ),
                ],
                "3-5": [
                    LineFore(colour=Colour.from_hex(0x8F8FA3), width=50),
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
                    LineFore(colour=Colour.from_hex(0x73738C), width=100, unrounded=True),
                    LineText(
                        colour=Colour.from_hex(0x73738C).darkened(),
                        arrow_colour=Colour.from_hex(0x73738C).darkened(),
                        size=20,
                    ),
                ],
                "2-5": [
                    LineFore(colour=Colour.from_hex(0x73738C), width=50, unrounded=True),
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
                    LineFore(colour=Colour.from_hex(0x73738C), width=200, unrounded=True),
                    LineText(
                        colour=Colour.from_hex(0x73738C).darkened(),
                        arrow_colour=Colour.from_hex(0x73738C).darkened(),
                        size=40,
                    ),
                ],
                "2-5": [
                    LineFore(colour=Colour.from_hex(0x73738C), width=100, unrounded=True),
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
                    AreaFill(colour=Colour.from_hex(0xFF99FF), outline=Colour.from_hex(0xFF99FF).darkened()),
                    AreaCentreText(colour=Colour.from_hex(0xFF99FF).darkened(), size=10),
                ]
            },
        )
    )
    
    types.append(
        ComponentType(
            name="plaza",
            shape="area",
            styles={
                "0-4": [
                    AreaFill(colour=Colour.from_hex(0xCCCCFF), outline=Colour.from_hex(0xCCCCFF).darkened()),
                    AreaCentreText(colour=Colour.from_hex(0xCCCCFF).darkened(), size=15),
                ],
                "5-6": [
                    AreaFill(colour=Colour.from_hex(0xCCCCFF), outline=Colour.from_hex(0xCCCCFF).darkened()),
                ]
            },
        )
    )

    for name, col in (
        ("building_underground", BUILDING),
        ("cityHall_underground", Colour.from_hex(0xffaaaa)),
        ("transportBuilding_underground", TRANSPORT_BUILDING),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="area",
                styles={
                    "0-1": [
                        AreaFill(colour=col.brightened(), outline=col),
                        AreaCentreText(colour=col.darkened(), size=15),
                    ],
                    "2-3": [
                        AreaFill(colour=col.brightened(), outline=col),
                    ]
                },
            )
        )

    types.append(
        ComponentType(
            name="park",
            shape="area",
            styles={
                "0-2": [
                    AreaFill(colour=Colour.from_hex(0x669900), outline=Colour.from_hex(0x669900).darkened()),
                    AreaCentreText(colour=Colour.from_hex(0x669900).darkened(), size=20),
                ],
                "3-6": [
                    AreaFill(colour=Colour.from_hex(0x669900), outline=Colour.from_hex(0x669900).darkened()),
                ]
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
                    LineBack(colour=Colour.from_hex(0xeeeeee), width=8),
                    LineFore(colour=Colour.from_hex(0x66ff66), width=4, dash=[16, 16]),
                    LineText(colour=Colour.from_hex(0xaaaaaa), arrow_colour=Colour.from_hex(0xeeeeee), size=16, offset=10)
                ]
            },
        )
    )

    for name, col, width, small_width in (
        ("localHighwaySlip_underground", LOCAL_HIGHWAY, 20, 1),
        ("bRoadSlip_underground", B_ROAD, 24, 2),
        ("aRoadSlip_underground", A_ROAD, 32, 3),
        ("localPedestrianQuaternaryRoad_underground", LOCAL_PEDESTRIAN, 16, 1),
        ("localQuaternaryRoad_underground", LOCAL_TERTIARY_QUATERNARY, 16, 1),
        ("localPedestrianTertiaryRoad_underground", LOCAL_PEDESTRIAN, 24, 2),
        ("localTertiaryRoad_underground", LOCAL_TERTIARY_QUATERNARY, 24, 2),
        ("localSecondaryRoad_underground", LOCAL_SECONDARY, 28, 2),
        ("localMainRoad_underground", LOCAL_MAIN, 32, 3),
        ("localHighway_underground", LOCAL_HIGHWAY, 36, 3),
        ("bRoad_underground", B_ROAD, 40, 4),
        ("aRoad_underground", A_ROAD, 48, 4),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(colour=col, width=width + 8),
                        LineFore(colour=col.brightened(), width=width),
                        LineText(colour=Colour.from_hex(0x000000), arrow_colour=col, size=width),
                    ],
                    "5-8": [
                        LineBack(colour=col, width=small_width * 2),
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
                    LineFore(colour=Colour.from_hex(0x808080), width=8, dash=[50, 25]),
                    LineText(colour=Colour.from_hex(0x808080), arrow_colour=Colour.from_hex(0x808080), offset=16, size=16),
                ],
                "3-4": [
                    LineFore(colour=Colour.from_hex(0x808080), width=2, dash=(20, 10))
                ]
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
                    LineFore(colour=Colour.from_hex(0x808080), width=16, dash=[50, 25]),
                    LineText(colour=Colour.from_hex(0x808080), arrow_colour=Colour.from_hex(0x808080), offset=16, size=16),
                ],
                "3-6": [
                    LineFore(colour=Colour.from_hex(0x808080), width=2, dash=(20, 10))
                ]
            },
        )
    )

    types.append(
        ComponentType(
            name="platform_underground",
            shape="area",
            styles={
                "0-1": [
                    AreaFill(colour=Colour.from_hex(0xaaaaaa), outline=Colour.from_hex(0xaaaaaa).darkened()),
                    AreaCentreText(Colour.from_hex(0xaaaaaa).darkened(), size=10)
                ],
                "2-3": [
                    AreaFill(colour=Colour.from_hex(0xaaaaaa), outline=Colour.from_hex(0xaaaaaa).darkened()),
                ]
            },
        )
    )

    
    for name, col in (
        ("building", BUILDING),
        ("cityHall", Colour.from_hex(0xffaaaa)),
        ("transportBuilding", TRANSPORT_BUILDING),
    ):
        types.append(
            ComponentType(
                name="building_underground",
                shape="area",
                styles={
                    "0-1": [
                        AreaFill(colour=col, outline=col),
                        AreaCentreText(colour=col.darkened(), size=15),
                    ],
                    "2-3": [
                        AreaFill(colour=col, outline=col),
                    ]
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
                    LineBack(colour=Colour.from_hex(0xeeeeee), width=8),
                    LineFore(colour=Colour.from_hex(0x008000), width=4, dash=[16, 16]),
                    LineText(colour=Colour.from_hex(0xaaaaaa), arrow_colour=Colour.from_hex(0xeeeeee), size=16, offset=10)
                ]
            },
        )
    )

    for name, col, width, small_width in (
        ("localHighwaySlip", LOCAL_HIGHWAY, 20, 1),
        ("bRoadSlip", B_ROAD, 24, 2),
        ("aRoadSlip", A_ROAD, 32, 3),
        ("localPedestrianQuaternaryRoad", LOCAL_PEDESTRIAN, 16, 1),
        ("localQuaternaryRoad", LOCAL_TERTIARY_QUATERNARY, 16, 1),
        ("localPedestrianTertiaryRoad", LOCAL_PEDESTRIAN, 24, 2),
        ("localTertiaryRoad", LOCAL_TERTIARY_QUATERNARY, 24, 2),
        ("localSecondaryRoad", LOCAL_SECONDARY, 28, 2),
        ("localMainRoad", LOCAL_MAIN, 32, 3),
        ("localHighway", LOCAL_HIGHWAY, 36, 3),
        ("bRoad", B_ROAD, 40, 4),
        ("aRoad", A_ROAD, 48, 4),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(colour=col.darkened(), width=width + 8),
                        LineFore(colour=col, width=width),
                        LineText(colour=Colour.from_hex(0x000000), arrow_colour=col, size=width),
                    ],
                    "5-8": [
                        LineBack(colour=col.darkened(), width=small_width * 2),
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
                    LineFore(colour=Colour.from_hex(0x808080), width=8),
                    LineText(colour=Colour.from_hex(0x808080), arrow_colour=Colour.from_hex(0x808080), offset=16, size=16),
                ],
                "3-4": [
                    LineFore(colour=Colour.from_hex(0x808080), width=2)
                ]
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
                    LineBack(colour=Colour.from_hex(0x808080), width=16),
                    LineFore(colour=Colour.from_hex(0xffffff), width=8, dash=[50, 50]),
                    LineText(colour=Colour.from_hex(0x808080), arrow_colour=Colour.from_hex(0x808080), offset=16, size=16),
                ],
                "3-6": [
                    LineBack(colour=Codour.from_hex(0x808080), width=4)
                    LineFore(colour=Colour.from_hex(0xffffff), width=2, dash=(20, 20))
                ]
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
                    LineBack(colour=Colour.from_hex(0x555555), width=12),
                    LineBack(colour=Colour.from_hex(0xeeeeee), width=8),
                    LineFore(colour=Colour.from_hex(0x008000), width=4, dash=[16, 16]),
                    LineText(colour=Colour.from_hex(0xaaaaaa), arrow_colour=Colour.from_hex(0xeeeeee), size=16, offset=10)
                ]
            },
        )
    )

    for name, col, width, small_width in (
        ("localHighwaySlip_elevated", LOCAL_HIGHWAY, 20, 1),
        ("bRoadSlip_elevated", B_ROAD, 24, 2),
        ("aRoadSlip_elevated", A_ROAD, 32, 3),
        ("localPedestrianQuaternaryRoad_elevated", LOCAL_PEDESTRIAN, 16, 1),
        ("localQuaternaryRoad_elevated", LOCAL_TERTIARY_QUATERNARY, 16, 1),
        ("localPedestrianTertiaryRoad_elevated", LOCAL_PEDESTRIAN, 24, 2),
        ("localTertiaryRoad_elevated", LOCAL_TERTIARY_QUATERNARY, 24, 2),
        ("localSecondaryRoad_elevated", LOCAL_SECONDARY, 28, 2),
        ("localMainRoad_elevated", LOCAL_MAIN, 32, 3),
        ("localHighway_elevated", LOCAL_HIGHWAY, 36, 3),
        ("bRoad_elevated", B_ROAD, 40, 4),
        ("aRoad_elevated", A_ROAD, 48, 4),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(colour=Colour.from_hex(0x555555), width=width + 8),
                        LineFore(colour=col, width=width),
                        LineText(colour=Colour.from_hex(0x000000), arrow_colour=col, size=width),
                    ],
                    "5-8": [
                        LineBack(colour=Colour.from_hex(0x555555), width=small_width * 2),
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
                    LineBack(colour=Colour.from_hex(0x555555), width=12),
                    LineFore(colour=Colour.from_hex(0x808080), width=8),
                    LineText(colour=Colour.from_hex(0x808080), arrow_colour=Colour.from_hex(0x808080), offset=16, size=16),
                ],
                "3-4": [
                    LineBack(colour=Colour.from_hex(0x555555), width=4),
                    LineFore(colour=Colour.from_hex(0x808080), width=2)
                ]
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
                    LineBack(colour=Colour.from_hex(0x555555), width=20),
                    LineBack(colour=Colour.from_hex(0x808080), width=16),
                    LineFore(colour=Colour.from_hex(0xffffff), width=8, dash=[50, 50]),
                    LineText(colour=Colour.from_hex(0x808080), arrow_colour=Colour.from_hex(0x808080), offset=16, size=16),
                ],
                "3-6": [
                    LineBack(colour=Colour.from_hex(0x555555), width=6),
                    LineBack(colour=Codour.from_hex(0x808080), width=4),
                    LineFore(colour=Colour.from_hex(0xffffff), width=2, dash=(20, 20))
                ]
            },
        )
    )

    types.append(
        ComponentType(
            name="platform",
            shape="area",
            styles={
                "0-1": [
                    AreaFill(colour=Colour.from_hex(0xcccccc), outline=Colour.from_hex(0x808080)),
                    AreaCentreText(Colour.from_hex(0x808080), size=10)
                ],
                "2-3": [
                    AreaFill(colour=Colour.from_hex(0xcccccc), outline=Colour.from_hex(0x808080)),
                ]
            },
        )
    )

    

    skin = Skin(
        name="default",
        fonts={
            "": [
                get_url(
                    "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Regular.ttf"
                )
            ],
            "b": [
                get_url(
                    "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Bold.ttf"
                )
            ],
            "i": [
                get_url(
                    "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-Italic.ttf"
                )
            ],
            "bi": [
                get_url(
                    "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/hinted/ttf/NotoSans-BoldItalic.ttf"
                )
            ],
        },
        background=LAND,
        types=types,
        licence=(Path(__file__).parent / "default_licences.md").read_text(),
    )
    skin.save_json(Path(__file__).parent)


if __name__ == "__main__":
    main()
