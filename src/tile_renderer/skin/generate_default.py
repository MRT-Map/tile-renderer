import re
import tempfile
from pathlib import Path

import niquests

from tile_renderer._logger import log
from tile_renderer.colour import Colour
from tile_renderer.coord import Vector
from tile_renderer.skin import (
    AreaBorderText,
    AreaCentreText,
    AreaFill,
    ComponentType,
    LineBack,
    LineFore,
    LineText,
    PointImage,
    PointSquare,
    PointText,
    Skin,
)


def get_url(url: str) -> tuple[str, bytes]:
    path = Path(tempfile.gettempdir()) / "tile-renderer" / "url" / url
    if path.exists():
        return url.split(".")[-1], path.read_bytes()
    response = niquests.get(url).content or b""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    path.write_bytes(response)
    return url.split(".")[-1], response


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


def main():
    log.info("Generating skin")
    types: list[ComponentType] = []

    for name, colour_hex in (
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
        colour = Colour.from_hex(colour_hex)
        types.append(
            ComponentType(
                name=name,
                shape="area",
                styles={
                    "0-3": [
                        AreaFill(colour=colour, outline=colour.darkened(20.0), outline_width=0.5),
                        AreaCentreText(colour=colour.darkened(20.0), size=5.0),
                    ],
                    "4-6": [AreaFill(colour=colour, outline=colour.darkened(20.0), outline_width=0.5 / (1.5 / 2) ** 4)],
                },
            )
        )

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
                    LineFore(colour=WATER, width=4.0),
                ],
            },
        )
    )

    types.append(
        ComponentType(
            name="ferryLine",
            shape="line",
            styles={
                "0-3": [
                    LineFore(colour=Colour.from_hex(0x25A7DA), width=1.0),
                    LineText(
                        colour=Colour.from_hex(0x25A7DA).darkened(), arrow_colour=Colour.from_hex(0x25A7DA), size=2.4
                    ),
                ],
                "4-6": [
                    LineFore(colour=Colour.from_hex(0x25A7DA), width=1.0 / (1.5 / 2) ** 4),
                ],
            },
        )
    )

    for name, colour_hex in (
        ("grass", 0xBBFF99),
        ("shrub", 0x99FF99),
        ("forest", 0x5CA904),
        ("stone", 0xAAAAAA),
        ("sand", 0xF7E1A1),
    ):
        colour = Colour.from_hex(colour_hex)
        types.append(
            ComponentType(
                name=name,
                shape="area",
                styles={
                    "0-3": [
                        AreaFill(colour=colour, outline=colour.darkened(20.0), outline_width=0.5),
                        AreaCentreText(colour=colour.darkened(40.0 if name == "sand" else 20.0), size=5.0),
                    ],
                    "4-6": [AreaFill(colour=colour, outline=colour.darkened(20.0), outline_width=0.5 / (1.5 / 2) ** 4)],
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
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-5": [
                    LineFore(colour=Colour.from_hex(0x8F8FA3), width=10.0 / (2 / 2) ** 3, zoom_multiplier=2.0),
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
                    LineFore(
                        colour=Colour.from_hex(0x73738C), width=20.0 / (2 / 2) ** 2, unrounded=True, zoom_multiplier=2.0
                    ),
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
                    LineFore(
                        colour=Colour.from_hex(0x73738C), width=40.0 / (2 / 2) ** 2, unrounded=True, zoom_multiplier=2.0
                    ),
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
                        outline=Colour.from_hex(0xCCCCFF).darkened(10.0),
                        outline_width=0.5,
                    ),
                    AreaCentreText(colour=Colour.from_hex(0xCCCCFF).darkened(10.0), size=3.0),
                ],
                "3-6": [
                    AreaFill(
                        colour=Colour.from_hex(0xCCCCFF),
                        outline=Colour.from_hex(0xCCCCFF).darkened(10.0),
                        outline_width=0.5 / (1.5 / 2) ** 3,
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
                        AreaFill(colour=col.brightened(), outline=col, outline_width=0.5 / (1.5 / 2) ** 3),
                    ],
                },
            )
        )

    types.append(
        ComponentType(
            name="park",
            shape="area",
            styles={
                "0-3": [
                    AreaFill(
                        colour=Colour.from_hex(0x669900),
                        outline=Colour.from_hex(0x669900).darkened(20.0),
                        outline_width=0.5,
                    ),
                    AreaCentreText(colour=Colour.from_hex(0x669900).darkened(20.0), size=4.0),
                ],
                "4-6": [
                    AreaFill(
                        colour=Colour.from_hex(0x669900),
                        outline=Colour.from_hex(0x669900).darkened(20.0),
                        outline_width=0.5 / (1.5 / 2) ** 4,
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
                    LineFore(colour=Colour.from_hex(0xEEEEEE), width=1.5, zoom_multiplier=2.0),
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

    for name, col, width in (
        ("localHighwaySlip_underground", LOCAL_HIGHWAY, 4.0),
        ("bRoadSlip_underground", B_ROAD, 4.8),
        ("aRoadSlip_underground", A_ROAD, 6.4),
        ("localPedestrianQuaternaryRoad_underground", LOCAL_PEDESTRIAN, 3.2),
        ("localQuaternaryRoad_underground", LOCAL_TERTIARY_QUATERNARY, 3.2),
        ("localPedestrianTertiaryRoad_underground", LOCAL_PEDESTRIAN, 4.8),
        ("localTertiaryRoad_underground", LOCAL_TERTIARY_QUATERNARY, 4.8),
        ("localSecondaryRoad_underground", LOCAL_SECONDARY, 5.6),
        ("localMainRoad_underground", LOCAL_MAIN, 6.4),
        ("localHighway_underground", LOCAL_HIGHWAY, 7.2),
        ("bRoad_underground", B_ROAD, 8.0),
        ("aRoad_underground", A_ROAD, 9.6),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(colour=col, width=width + 1.6, zoom_multiplier=2),
                        LineFore(
                            colour=col.brightened(10.0 if "Pedestrian" in name else 30.0),
                            width=width,
                            zoom_multiplier=2,
                        ),
                        LineText(
                            colour=Colour.from_hex(0x000000), arrow_colour=col.darkened(), size=width, zoom_multiplier=2
                        ),
                    ],
                    "5-8": [
                        LineBack(colour=col, width=width * 1.5 * 1.5),
                        LineFore(colour=col.brightened(10.0 if "Pedestrian" in name else 30.0), width=width * 1.5),
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
                    LineText(colour=Colour.from_hex(0x111111), arrow_colour=Colour.from_hex(0x111111), size=3.2),
                ],
                "3-6": [LineFore(colour=Colour.from_hex(0x808080), width=3.0, dash=[20.0, 10.0])],
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
                        colour=Colour.from_hex(0x111111),
                        arrow_colour=Colour.from_hex(0x111111),
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [LineFore(colour=Colour.from_hex(0x808080), width=6.4, dash=[20.0, 10.0], zoom_multiplier=2.0)],
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
                        outline_width=0.5 / (1.5 / 2) ** 2,
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
                        AreaFill(colour=col, outline=col.darkened(), outline_width=0.5 / (1.5 / 2) ** 3),
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
                    LineFore(colour=Colour.from_hex(0xEEEEEE), width=1.5, zoom_multiplier=2.0),
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

    for name, col, width in (
        ("localHighwaySlip", LOCAL_HIGHWAY, 4.0),
        ("bRoadSlip", B_ROAD, 4.8),
        ("aRoadSlip", A_ROAD, 6.4),
        ("localPedestrianQuaternaryRoad", LOCAL_PEDESTRIAN, 3.2),
        ("localQuaternaryRoad", LOCAL_TERTIARY_QUATERNARY, 3.2),
        ("localPedestrianTertiaryRoad", LOCAL_PEDESTRIAN, 4.8),
        ("localTertiaryRoad", LOCAL_TERTIARY_QUATERNARY, 4.8),
        ("localSecondaryRoad", LOCAL_SECONDARY, 5.6),
        ("localMainRoad", LOCAL_MAIN, 6.4),
        ("localHighway", LOCAL_HIGHWAY, 3.6),
        ("bRoad", B_ROAD, 8.0),
        ("aRoad", A_ROAD, 9.6),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(
                            colour=col.darkened(10.0 if "Pedestrian" in name else 30.0),
                            width=width + 1.6,
                            zoom_multiplier=2,
                        ),
                        LineFore(colour=col, width=width, zoom_multiplier=2),
                        LineText(
                            colour=Colour.from_hex(0x000000), arrow_colour=col.darkened(), size=width, zoom_multiplier=2
                        ),
                    ],
                    "5-8": [
                        LineBack(colour=col.darkened(10.0 if "Pedestrian" in name else 30.0), width=width * 1.5 * 1.5),
                        LineFore(colour=col, width=width * 1.5),
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
                        colour=Colour.from_hex(0x111111),
                        arrow_colour=Colour.from_hex(0x111111),
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [LineFore(colour=Colour.from_hex(0x808080), width=3.0, zoom_multiplier=2.0)],
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
                    LineFore(colour=Colour.from_hex(0x808080), width=3.2, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=1.6, dash=[10.0, 10.0], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x111111),
                        arrow_colour=Colour.from_hex(0x111111),
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [
                    LineFore(colour=Colour.from_hex(0x808080), width=6.4),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=3.2, dash=[20.0, 20.0]),
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
                    LineBack(colour=Colour.from_hex(0x333333), width=2.4, zoom_multiplier=2.0, unrounded=True),
                    LineFore(colour=Colour.from_hex(0xEEEEEE), width=1.5, zoom_multiplier=2.0),
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

    for name, col, width in (
        ("localHighwaySlip_elevated", LOCAL_HIGHWAY, 4.0),
        ("bRoadSlip_elevated", B_ROAD, 4.8),
        ("aRoadSlip_elevated", A_ROAD, 6.4),
        ("localPedestrianQuaternaryRoad_elevated", LOCAL_PEDESTRIAN, 3.2),
        ("localQuaternaryRoad_elevated", LOCAL_TERTIARY_QUATERNARY, 3.2),
        ("localPedestrianTertiaryRoad_elevated", LOCAL_PEDESTRIAN, 4.8),
        ("localTertiaryRoad_elevated", LOCAL_TERTIARY_QUATERNARY, 4.8),
        ("localSecondaryRoad_elevated", LOCAL_SECONDARY, 5.6),
        ("localMainRoad_elevated", LOCAL_MAIN, 6.4),
        ("localHighway_elevated", LOCAL_HIGHWAY, 7.2),
        ("bRoad_elevated", B_ROAD, 8.0),
        ("aRoad_elevated", A_ROAD, 9.6),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="line",
                tags=["road"],
                styles={
                    "0-4": [
                        LineBack(
                            colour=col.darkened(10.0 if "Pedestrian" in name else 30.0),
                            width=width + 1.6,
                            zoom_multiplier=2,
                        ),
                        LineBack(
                            colour=Colour.from_hex(0x333333), width=width + 1.6, zoom_multiplier=2, unrounded=True
                        ),
                        LineFore(colour=col, width=width, zoom_multiplier=2),
                        LineText(
                            colour=Colour.from_hex(0x000000), arrow_colour=col.darkened(), size=width, zoom_multiplier=2
                        ),
                    ],
                    "5-8": [
                        LineBack(colour=col.darkened(10.0 if "Pedestrian" in name else 30.0), width=width * 1.5 * 1.5),
                        LineBack(colour=Colour.from_hex(0x333333), width=width * 1.5 * 1.5, unrounded=True),
                        LineFore(colour=col, width=width * 1.5),
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
                    LineBack(colour=Colour.from_hex(0x333333), width=2.4, zoom_multiplier=2.0, unrounded=True),
                    LineFore(colour=Colour.from_hex(0x808080), width=1.6, zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x111111),
                        arrow_colour=Colour.from_hex(0x111111),
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [
                    LineBack(colour=Colour.from_hex(0x333333), width=6.4, unrounded=True),
                    LineFore(colour=Colour.from_hex(0x808080), width=3.2),
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
                    LineBack(colour=Colour.from_hex(0x333333), width=4.8, zoom_multiplier=2.0, unrounded=True),
                    LineFore(colour=Colour.from_hex(0x808080), width=3.2, zoom_multiplier=2.0),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=1.6, dash=[10.0, 10.0], zoom_multiplier=2.0),
                    LineText(
                        colour=Colour.from_hex(0x111111),
                        arrow_colour=Colour.from_hex(0x111111),
                        size=3.2,
                        zoom_multiplier=2.0,
                    ),
                ],
                "3-6": [
                    LineBack(colour=Colour.from_hex(0x333333), width=9.6, unrounded=True),
                    LineFore(colour=Colour.from_hex(0x808080), width=6.4),
                    LineFore(colour=Colour.from_hex(0xFFFFFF), width=3.2, dash=[20.0, 20.0]),
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
                    AreaFill(
                        colour=Colour.from_hex(0xCCCCCC),
                        outline=Colour.from_hex(0x808080),
                        outline_width=0.5 / (1.5 / 2) ** 2,
                    ),
                ],
            },
        )
    )

    for name, image_path, extension, colour_hex in (
        ("pedestrianCrossing", Path(__file__).parent / "default_icons" / "traffic-light.svg", "svg+xml", 0x000000),
        ("railCrossing", Path(__file__).parent / "default_icons" / "train.svg", "svg+xml", 0x000000),
        ("parking", Path(__file__).parent / "default_icons" / "square-parking.svg", "svg+xml", 0x000000),
        ("bikeRack", Path(__file__).parent / "default_icons" / "bicycle.svg", "svg+xml", 0x000000),
        ("shop", Path(__file__).parent / "default_icons" / "store.svg", "svg+xml", 0x000000),
        ("restaurant", Path(__file__).parent / "default_icons" / "utensils.svg", "svg+xml", 0x000000),
        ("hotel", Path(__file__).parent / "default_icons" / "bed.svg", "svg+xml", 0x000000),
        ("arcade", Path(__file__).parent / "default_icons" / "gamepad.svg", "svg+xml", 0x000000),
        ("supermarket", Path(__file__).parent / "default_icons" / "cart-shopping.svg", "svg+xml", 0x000000),
        ("clinic", Path(__file__).parent / "default_icons" / "house-chimney-medical.svg", "svg+xml", 0x000000),
        ("library", Path(__file__).parent / "default_icons" / "book.svg", "svg+xml", 0x000000),
        ("placeOfWorship", Path(__file__).parent / "default_icons" / "place-of-worship.svg", "svg+xml", 0x000000),
        ("petrol", Path(__file__).parent / "default_icons" / "gas-pump.svg", "svg+xml", 0x000000),
        ("cinema", Path(__file__).parent / "default_icons" / "film.svg", "svg+xml", 0x000000),
        ("bank", Path(__file__).parent / "default_icons" / "building-columns.svg", "svg+xml", 0x000000),
        ("gym", Path(__file__).parent / "default_icons" / "dumbbell.svg", "svg+xml", 0x000000),
        ("shelter", Path(__file__).parent / "default_icons" / "people-roof.svg", "svg+xml", 0x000000),
        ("playground", Path(__file__).parent / "default_icons" / "baseball-bat-ball.svg", "svg+xml", 0x000000),
        ("waterFeature", Path(__file__).parent / "default_icons" / "droplet.svg", "svg+xml", 0x000000),
        ("transportExit", Path(__file__).parent / "default_icons" / "right-from-bracket.svg", "svg+xml", 0x000000),
        ("attraction", Path(__file__).parent / "default_icons" / "camera.svg", "svg+xml", 0x000000),
        ("airport", Path(__file__).parent / "default_icons" / "plane.svg", "svg+xml", 0x1F3D7A),
    ):
        result = re.search(r'viewBox="0 0 ([^ ]*) ([^ ]*?)"', image_path.read_text())
        if result is None:
            raise ValueError(image_path)
        width = int(result.group(1))
        height = int(result.group(2))
        colour = Colour.from_hex(colour_hex)
        types.append(
            ComponentType(
                name=name,
                shape="point",
                styles={
                    "0-5": [
                        PointImage(
                            image=image_path.read_bytes(), extension=extension, size=Vector(5.0, height / width * 5.0)
                        ),
                        PointText(colour=colour, offset=Vector(0.0, 5.0), size=2.5),
                    ]
                },
            )
        )

    for name, colour in (
        ("busStop", Colour.from_hex(0x00AAFF)),
        ("ferryStop", Colour.from_hex(0x1E85AE)),
        ("railStation", Colour.from_hex(0x1F3D7A)),
    ):
        types.append(
            ComponentType(
                name=name,
                shape="point",
                styles={
                    "0-3": [
                        PointSquare(colour=colour, size=2.5, width=0),
                        PointText(colour=colour.darkened(10.0), offset=Vector(0.0, 4.0), size=2.5),
                    ],
                    "4-6": [
                        PointSquare(colour=colour, size=2.5 / (1.5 / 2) ** 4, width=0),
                    ],
                },
            )
        )

    for name, zoom, colour_hex, size in (
        ("subdistrict", 2, 0xD9B38C, 2.0),
        ("district", 3, 0xCC9966, 2.5),
        ("town", 3, 0xBF8040, 3.0),
        ("state", 4, 0x996633, 3.5),
        ("country", 4, 0x86592D, 4.0),
    ):
        colour = Colour.from_hex(colour_hex)
        types.append(
            ComponentType(
                name=name,
                shape="area",
                styles={
                    "0-" + str(zoom): [
                        AreaFill(outline=colour, outline_width=0.5),
                        AreaBorderText(colour=colour.darkened(), offset=2.0, size=4.0),
                    ],
                    str(zoom) + "-" + str(zoom + 3): [
                        AreaFill(outline=colour, outline_width=0.5 / (1.5 / 2) ** zoom),
                        AreaCentreText(colour=colour.darkened(), size=size / (1.0 / 2) ** zoom, zoom_multiplier=1.0),
                        AreaBorderText(
                            colour=colour.darkened(), offset=2.0 / (1.5 / 2) ** zoom, size=4.0 / (1.5 / 2) ** zoom
                        ),
                    ],
                },
            )
        )
        types.append(
            ComponentType(
                name=name + "Marker",
                shape="point",
                styles={
                    str(zoom) + "-" + str(zoom + 3): [
                        PointText(colour=colour.darkened(), size=size / (1.0 / 2) ** zoom, zoom_multiplier=1.0),
                    ]
                },
            )
        )

    types.append(
        ComponentType(
            name="simpleArea",
            shape="area",
            styles={
                "0-5": [
                    AreaFill(colour=Colour.from_hex(0xAAAAAA), outline=Colour.from_hex(0x808080)),
                    AreaCentreText(colour=Colour.from_hex(0x555555), size=10.0),
                    AreaBorderText(colour=Colour.from_hex(0x555555), offset=2.0, size=4.0),
                ]
            },
        )
    )

    types.append(
        ComponentType(
            name="simpleLine", shape="line", styles={"0-5": [LineFore(colour=Colour.from_hex(0x555555), width=1.5)]}
        )
    )

    types.append(
        ComponentType(
            name="simplePoint",
            shape="point",
            styles={
                "0-5": [
                    PointSquare(colour=Colour.from_hex(0xAAAAAA), size=5.0, width=1.2),
                    PointText(colour=Colour.from_hex(0x808080), offset=Vector(0.0, 5.0), size=5.0),
                ]
            },
        )
    )

    skin = Skin(
        name="default",
        font_files=[
            get_url(
                "https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io/fonts/NotoSans/full/ttf/NotoSans-Bold.ttf"
            ),
            get_url(
                "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Black.otf",
            ),
        ],
        font_string="'Noto Sans', 'Noto Sans CJK JP'",
        background=LAND,
        types=types,
        prune_small_text=1.0,
        licence=(Path(__file__).parent / "default_licences.md").read_text(),
    )
    skin.save_json(Path(__file__).parent)


if __name__ == "__main__":
    main()
