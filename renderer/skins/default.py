# noqa: INP001

import json
from math import ceil
from pathlib import Path

from renderer.misc_types.skin_builder import CS, CTI, SkinBuilder, brighten, darken

A_ROAD = 0xFFAAAA
B_ROAD = 0xFF8000
LOCAL_HIGHWAY = 0xFFCC80
LOCAL_MAIN = 0xFFEE00
LOCAL_SECONDARY = 0xFFF899
LOCAL_TERTIARY_QUATERNARY = 0xEEEEEE
LOCAL_PEDESTRIAN = 0xCCCCFF
BUILDING = 0xA2A288
TRANSPORT_BUILDING = 0x999966


def main() -> None:  # noqa: PLR0912, PLR0915
    s = SkinBuilder(
        256,
        {
            "": [
                Path("ClearSans-Medium.ttf"),
                Path("NotoSans-Medium.ttf"),
                Path("NotoSansSC-Medium.ttf"),
            ],
            "b": [
                Path("ClearSans-Bold.ttf"),
                Path("NotoSans-Bold.ttf"),
                Path("NotoSansSC-Bold.ttf"),
            ],
            "i": [
                Path("ClearSans-MediumItalic.ttf"),
                Path("NotoSans-MediumItalic.ttf"),
                Path("NotoSansSC-Medium.ttf"),
            ],
            "bi": [
                Path("ClearSans-BoldItalic.ttf"),
                Path("NotoSans-BoldItalic.ttf"),
                Path("NotoSansSC-Bold.ttf"),
            ],
        },
        0xDDDDDD,
    )

    for name, col in (
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
        area = CTI("area")
        for i, size in ((0, 30), (1, 20), (2, 10)):
            area[i] = [
                CS.area_fill(colour=col),
                CS.area_centertext(colour=darken(col), size=size),
            ]
        area[3:6] = [CS.area_fill(colour=col)]
        s[name] = area

    water_large = CTI("area")
    water_large[0:] = [
        CS.area_fill(colour=0x87CEEB),
        CS.area_centertext(colour=darken(0x87CEEB), size=50),
    ]
    s["waterLarge"] = water_large

    water_small = CTI("area")
    water_small[0:2] = [
        CS.area_fill(colour=0x87CEEB),
        CS.area_centertext(colour=darken(0x87CEEB), size=25),
    ]
    water_small[3:] = [CS.area_fill(colour=0x87CEEB)]
    s["waterSmall"] = water_small

    land_large = CTI("area")
    land_large[0:2] = [
        CS.area_fill(colour=0xDDDDDD),
        CS.area_centertext(colour=0x808080, size=50),
    ]
    land_large[3:5] = [
        CS.area_fill(colour=0xDDDDDD),
        CS.area_centertext(colour=0x808080, size=50),
    ]
    land_large[6:] = [CS.area_fill(colour=0xDDDDDD)]
    s["landLarge"] = land_large

    land_small = CTI("area")
    land_small[0:2] = [
        CS.area_fill(colour=0xDDDDDD),
        CS.area_centertext(colour=0x808080, size=25),
    ]
    land_small[3:] = [CS.area_fill(colour=0xDDDDDD)]
    s["landSmall"] = land_small

    waterway = CTI("line")
    for i, width, size in ((0, 10, 20), (1, 7, 13), (2, 5, 10)):
        waterway[i] = [
            CS.line_fore(colour=0x87CEEB, width=width),
            CS.line_text(
                colour=darken(0x87CEEB),
                arrow_colour=darken(0x87CEEB, 0.25),
                size=size,
            ),
        ]
    waterway[3:4] = [
        CS.line_fore(colour=0x87CEEB, width=3),
    ]
    s["waterway"] = waterway

    ferry_line = CTI("line")
    ferry_line[0:3] = [
        CS.line_fore(colour=0x25A7DA, width=5),
        CS.line_text(colour=darken(0x25A7DA), arrow_colour=0x25A7DA, size=12),
    ]
    s["ferryLine"] = ferry_line

    for name, colour in (
        ("grass", 0xBBFF99),
        ("shrub", 0x99FF99),
        ("forest", 0x5CA904),
        ("stone", 0xAAAAAA),
        ("sand", 0xF7E1A1),
    ):
        area = CTI("area")
        for i, size in ((0, 25), (1, 20), (2, 15), (3, 10)):
            area[i] = [
                CS.area_fill(colour=colour, outline=darken(colour, 0.1)),
                CS.area_centertext(colour=darken(colour), size=size),
            ]
        area[4:6] = [
            CS.area_fill(colour=colour, outline=darken(colour, 0.1)),
        ]
        s[name] = area

    gate = CTI("area")
    gate[0:2] = [
        CS.area_fill(outline=0x33334D),
        CS.area_centertext(colour=0x33334D, size=10),
    ]
    gate[3:5] = [
        CS.area_fill(outline=0x33334D),
    ]
    s["gate"] = gate

    apron = CTI("area")
    apron[0:5] = [
        CS.area_fill(colour=0xC2C2D6),
        CS.area_centertext(colour=0x33334D, size=15),
    ]
    s["apron"] = apron

    taxiway = CTI("line")
    for i, width, size in ((0, 50, 20), (1, 25, 10), (2, 13, 5)):
        taxiway[i] = [
            CS.line_fore(colour=0x8F8FA3, width=width),
            CS.line_text(colour=0x33334D, arrow_colour=0x8F8FA3, size=size),
        ]
    for i, width in ((3, 10), (4, 7), (5, 5)):
        taxiway[i] = [CS.line_fore(colour=0x8F8FA3, width=width)]
    s["taxiway"] = taxiway

    runway = CTI("line", ["unroundedEnds"])
    for i, width, size in ((0, 100, 20), (1, 50, 10)):
        runway[i] = [
            CS.line_fore(colour=0x73738C, width=width),
            CS.line_text(colour=0x33334D, arrow_colour=0x73738C, size=size),
        ]
    for i, width in ((2, 25), (3, 13), (4, 6), (5, 3)):
        runway[i] = [CS.line_fore(colour=0x73738C, width=width)]
    s["runway"] = runway

    wide_runway = CTI("line", ["unroundedEnds"])
    for i, width, size in ((0, 200, 40), (1, 100, 20), (2, 50, 10)):
        wide_runway[i] = [
            CS.line_fore(colour=0x73738C, width=width),
            CS.line_text(colour=0x33334D, arrow_colour=0x73738C, size=size),
        ]
    for i, width in ((3, 25), (4, 13), (5, 6)):
        wide_runway[i] = [CS.line_fore(colour=0x73738C, width=width)]
    s["wideRunway"] = wide_runway

    helipad = CTI("area")
    helipad[0:1] = [
        CS.area_fill(colour=0xFF99FF, outline=0xFF66FF),
        CS.area_centertext(colour=0xFF66FF, size=10),
    ]
    s["helipad"] = helipad

    plaza = CTI("area")
    plaza[0:4] = [
        CS.area_fill(colour=0xCCCCFF, outline=0xBBBBBB),
        CS.area_centertext(colour=0x000000, size=15),
    ]
    s["plaza"] = plaza

    building_underground = CTI("area")
    building_underground[0:1] = [
        CS.area_fill(colour=brighten(BUILDING), outline=BUILDING),
        CS.area_centertext(colour=darken(BUILDING), size=15),
    ]
    building_underground[2:3] = [
        CS.area_fill(colour=brighten(BUILDING), outline=BUILDING),
    ]
    s["building_underground"] = building_underground

    city_hall = CTI("area")
    city_hall[0:1] = [
        CS.area_fill(colour=brighten(0xFFAAAA), outline=0xFFAAAA),
        CS.area_centertext(colour=darken(0xFFAAAA), size=15),
    ]
    city_hall[2:3] = [
        CS.area_fill(colour=brighten(0xFFAAAA), outline=0xFFAAAA),
    ]
    s["cityHall"] = city_hall

    transport_building_underground = CTI("area")
    transport_building_underground[0:1] = [
        CS.area_fill(colour=brighten(TRANSPORT_BUILDING), outline=TRANSPORT_BUILDING),
        CS.area_centertext(colour=darken(TRANSPORT_BUILDING), size=15),
    ]
    transport_building_underground[2:3] = [
        CS.area_fill(colour=brighten(TRANSPORT_BUILDING), outline=TRANSPORT_BUILDING),
    ]
    s["transportBuilding_underground"] = transport_building_underground

    park = CTI("area")
    park[0:2] = [
        CS.area_fill(colour=0x669900, outline=darken(0x669900, 0.1)),
        CS.area_centertext(colour=darken(0x669900), size=20),
    ]
    park[3:6] = [
        CS.area_fill(colour=0x669900, outline=darken(0x669900, 0.1)),
    ]
    s["park"] = park

    pathway_underground = CTI("line", ["road"])
    for i, width, dash, size, offset in (
        (0, 4, 16, 16, 10),
        (1, 4, 16, 16, 10),
        (2, 3, 12, 0, 0),
        (3, 2, 8, 0, 0),
        (4, 1, 4, 0, 0),
    ):
        pathway_underground[i] = [
            CS.line_back(colour=0xEEEEEE, width=width * 2),
            CS.line_fore(colour=0x66FF66, width=width, dash=(dash, dash)),
            *(
                [
                    CS.line_text(
                        colour=0xAAAAAA,
                        arrow_colour=0xEEEEEE,
                        size=size,
                        offset=offset,
                    ),
                ]
                if offset != 0
                else []
            ),
        ]
    s["pathway_underground"] = pathway_underground

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
        area = CTI("line", ["road"])
        for i in (0, 1, 2, 3, 4):
            area[i] = [
                CS.line_back(colour=col, width=int((width + 8) * (2 / 3) ** i)),
                CS.line_fore(colour=brighten(col), width=int(width * (2 / 3) ** i)),
                *(
                    [
                        CS.line_text(
                            colour=0x000000,
                            arrow_colour=col,
                            size=int(width * (2 / 3) ** i),
                        ),
                    ]
                    if width * (2 / 3) ** i > 12
                    else []
                ),
            ]
        for i in (5, 6, 7, 8, 9):
            area[i] = (
                [
                    CS.line_back(colour=col, width=(small_width - i + 5) * 2),
                    CS.line_fore(colour=brighten(col), width=small_width - i + 5),
                ]
                if small_width - i + 5 >= 1
                else []
            )
        s[name] = area

    rail_underground = CTI("line", ["road"])
    for i, width, dash, size in ((0, 8, 50, 16), (1, 6, 40, 13), (2, 4, 30, 10)):
        rail_underground[i] = [
            CS.line_fore(colour=0x808080, width=width, dash=(dash, dash // 2)),
            CS.line_text(
                colour=0x808080,
                arrow_colour=0x808080,
                offset=size,
                size=size,
            ),
        ]
    rail_underground[3:4] = [CS.line_fore(colour=0x808080, width=2, dash=(20, 10))]
    s["rail_underground"] = rail_underground

    intercity_rail_underground = CTI("line", ["road"])
    for i, width, dash, size in ((0, 8, 50, 16), (1, 6, 40, 13), (2, 4, 30, 10)):
        intercity_rail_underground[i] = [
            CS.line_fore(colour=0x808080, width=width * 2, dash=(dash, dash)),
            CS.line_text(
                colour=0x808080,
                arrow_colour=0x808080,
                offset=size,
                size=size,
            ),
        ]
    intercity_rail_underground[3:6] = [
        CS.line_fore(colour=0x808080, width=4, dash=(20, 20)),
    ]
    s["intercityRail_underground"] = intercity_rail_underground

    platform_underground = CTI("area")
    platform_underground[0:1] = [
        CS.area_fill(colour=0xAAAAAA, outline=darken(0xAAAAAA)),
        CS.area_centertext(colour=darken(0xAAAAAA), size=10),
    ]
    platform_underground[2:3] = [
        CS.area_fill(colour=0xAAAAAA, outline=darken(0xAAAAAA)),
    ]
    s["platform_underground"] = platform_underground

    building = CTI("area")
    building[0:1] = [
        CS.area_fill(colour=BUILDING, outline=darken(BUILDING)),
        CS.area_centertext(colour=darken(BUILDING), size=15),
    ]
    building[2:3] = [CS.area_fill(colour=BUILDING, outline=darken(BUILDING))]
    s["building"] = building

    city_hall = CTI("area")
    city_hall[0:1] = [
        CS.area_fill(colour=0xFFAAAA, outline=darken(0xFFAAAA)),
        CS.area_centertext(colour=darken(0xFFAAAA), size=15),
    ]
    city_hall[2:3] = [
        CS.area_fill(colour=0xFFAAAA, outline=darken(0xFFAAAA)),
    ]
    s["cityHall"] = city_hall

    transport_building = CTI("area")
    transport_building[0:1] = [
        CS.area_fill(colour=TRANSPORT_BUILDING, outline=darken(TRANSPORT_BUILDING)),
        CS.area_centertext(colour=darken(TRANSPORT_BUILDING), size=15),
    ]
    transport_building[2:3] = [
        CS.area_fill(colour=TRANSPORT_BUILDING, outline=darken(TRANSPORT_BUILDING)),
    ]
    s["transportBuilding"] = transport_building

    pathway = CTI("line", ["road"])
    for i, width, dash, size, offset in (
        (0, 4, 16, 16, 10),
        (1, 4, 16, 16, 10),
        (2, 3, 12, 0, 0),
        (3, 2, 8, 0, 0),
        (4, 1, 4, 0, 0),
    ):
        pathway[i] = [
            CS.line_back(colour=0xEEEEEE, width=width * 2),
            CS.line_fore(colour=0x008000, width=width, dash=(dash, dash)),
            *(
                [
                    CS.line_text(
                        colour=0xAAAAAA,
                        arrow_colour=0x008000,
                        size=size,
                        offset=offset,
                    ),
                ]
                if offset != 0
                else []
            ),
        ]
    s["pathway"] = pathway

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
        area = CTI("line", ["road"])
        for i in (0, 1, 2, 3, 4):
            area[i] = [
                CS.line_back(
                    colour=darken(col, 0.25),
                    width=int((width + 8) * (2 / 3) ** i),
                ),
                CS.line_fore(colour=col, width=int(width * (2 / 3) ** i)),
                *(
                    [
                        CS.line_text(
                            colour=0x000000,
                            arrow_colour=darken(col, 0.25),
                            size=int(width * (2 / 3) ** i),
                        ),
                    ]
                    if width * (2 / 3) ** i > 12
                    else []
                ),
            ]
        for i in (5, 6, 7, 8, 9):
            area[i] = (
                [
                    CS.line_back(
                        colour=darken(col, 0.25),
                        width=(small_width - i + 5) * 2,
                    ),
                    CS.line_fore(colour=col, width=small_width - i + 5),
                ]
                if small_width - i + 5 >= 1
                else []
            )
        s[name] = area

    rail = CTI("line", ["road"])
    for i, width, size in ((0, 8, 16), (1, 6, 13), (2, 4, 10)):
        rail[i] = [
            CS.line_fore(colour=0x808080, width=width),
            CS.line_text(
                colour=0x808080,
                arrow_colour=0x808080,
                offset=size,
                size=size,
            ),
        ]
    rail[3:4] = [CS.line_fore(colour=0x808080, width=2)]
    s["rail"] = rail

    intercity_rail = CTI("line", ["road"])
    for i, width, dash, size in ((0, 8, 50, 16), (1, 6, 40, 13), (2, 4, 30, 10)):
        intercity_rail[i] = [
            CS.line_back(colour=0x808080, width=width * 2),
            CS.line_fore(colour=0xFFFFFF, width=width, dash=(dash, dash)),
            CS.line_text(
                colour=0x808080,
                arrow_colour=0x808080,
                offset=size,
                size=size,
            ),
        ]
    intercity_rail[3:6] = [
        CS.line_back(colour=0x808080, width=4),
        CS.line_fore(colour=0xFFFFFF, width=2, dash=(20, 20)),
    ]
    s["intercityRail"] = intercity_rail

    pathway_elevated = CTI("line", ["road"])
    for i, width, dash, size, offset in (
        (0, 4, 16, 16, 10),
        (1, 4, 16, 16, 10),
        (2, 3, 12, 0, 0),
        (3, 2, 8, 0, 0),
        (4, 1, 4, 0, 0),
    ):
        pathway_elevated[i] = [
            CS.line_back(colour=0x000000, width=width * 3),
            CS.line_back(colour=0xEEEEEE, width=width * 2),
            CS.line_fore(colour=0x008000, width=width, dash=(dash, dash)),
            *(
                [
                    CS.line_text(
                        colour=0xAAAAAA,
                        arrow_colour=0x008000,
                        size=size,
                        offset=offset,
                    ),
                ]
                if offset != 0
                else []
            ),
        ]
    s["pathway_elevated"] = pathway_elevated

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
        area = CTI("line", ["road"])
        for i in (0, 1, 2, 3, 4):
            area[i] = [
                CS.line_back(colour=0x000000, width=int((width + 8) * (2 / 3) ** i)),
                CS.line_fore(colour=col, width=int(width * (2 / 3) ** i)),
                *(
                    [
                        CS.line_text(
                            colour=0x000000,
                            arrow_colour=darken(col, 0.25),
                            size=int(width * (2 / 3) ** i),
                        ),
                    ]
                    if width * (2 / 3) ** i > 12
                    else []
                ),
            ]
        for i in (5, 6, 7, 8, 9):
            area[i] = (
                [
                    CS.line_back(colour=0x000000, width=(small_width - i + 5) * 2),
                    CS.line_fore(colour=col, width=small_width - i + 5),
                ]
                if small_width - i + 5 >= 1
                else []
            )
        s[name] = area

    rail_elevated = CTI("line", ["road"])
    for i, width, size in ((0, 8, 16), (1, 6, 13), (2, 4, 10)):
        rail_elevated[i] = [
            CS.line_back(colour=0x000000, width=ceil(1.5 * width)),
            CS.line_fore(colour=0x808080, width=width),
            CS.line_text(
                colour=0x808080,
                arrow_colour=0x808080,
                offset=size,
                size=size,
            ),
        ]
    rail_elevated[3:4] = rail_elevated[i] = [
        CS.line_back(colour=0x000000, width=4),
        CS.line_fore(colour=0x808080, width=2),
    ]
    s["rail_elevated"] = rail_elevated

    intercity_rail_elevated = CTI("line", ["road"])
    for i, width, dash, size in ((0, 8, 50, 16), (1, 6, 40, 13), (2, 4, 30, 10)):
        intercity_rail_elevated[i] = [
            CS.line_back(colour=0x000000, width=width * 2),
            CS.line_fore(colour=0xFFFFFF, width=width, dash=(dash, dash)),
            CS.line_text(
                colour=0x808080,
                arrow_colour=0x808080,
                offset=size,
                size=size,
            ),
        ]
    intercity_rail_elevated[3:6] = [
        CS.line_back(colour=0x000000, width=4),
        CS.line_fore(colour=0xFFFFFF, width=2, dash=(20, 20)),
    ]
    s["intercityRail_elevated"] = intercity_rail_elevated

    platform = CTI("area")
    platform[0:1] = [
        CS.area_fill(colour=0xCCCCCC, outline=0x808080),
        CS.area_centertext(colour=0x808080, size=10),
    ]
    platform[2:3] = [
        CS.area_fill(colour=0xCCCCCC, outline=0x808080),
    ]
    s["platform"] = platform

    """pedestrian_crossing = CTI("point")
    pedestrian_crossing[0:5] = [
        CS.point_image(file=Path("pedestriancrossing.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['pedestrianCrossing'] = pedestrian_crossing

    rail_crossing = CTI("point")
    rail_crossing[0:5] = [
        CS.point_image(file=Path("pedestriancrossing.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['railCrossing'] = rail_crossing

    parking = CTI("point")
    parking[0:5] = [
        CS.point_image(file=Path("parking.png")),
        CS.point_text(colour=0x0000dc,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['parking'] = parking

    bike_rack = CTI("point")
    bike_rack[0:5] = [
        CS.point_image(file=Path("bikerack.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['bikeRack'] = bike_rack

    shop = CTI("point")
    shop[0:5] = [
        CS.point_image(file=Path("shop.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['shop'] = shop

    restaurant = CTI("point")
    restaurant[0:5] = [
        CS.point_image(file=Path("restaurant.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['restaurant'] = restaurant

    hotel = CTI("point")
    hotel[0:5] = [
        CS.point_image(file=Path("hotel.png")),
        CS.point_text(colour=0x0000fc,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['hotel'] = hotel

    arcade = CTI("point")
    arcade[0:5] = [
        CS.point_image(file=Path("arcade.png")),
        CS.point_text(colour=0xffdc00,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['arcade'] = arcade

    supermarket = CTI("point")
    supermarket[0:5] = [
        CS.point_image(file=Path("supermarket.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['supermarket'] = supermarket

    clinic = CTI("point")
    clinic[0:5] = [
        CS.point_image(file=Path("clinic.png")),
        CS.point_text(colour=0xff0303,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['clinic'] = clinic

    library = CTI("point")
    library[0:5] = [
        CS.point_image(file=Path("library.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['library'] = library

    place_of_worship = CTI("point")
    place_of_worship[0:5] = [
        CS.point_image(file=Path("placeofworship.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['placeOfWorship'] = place_of_worship

    petrol = CTI("point")
    petrol[0:5] = [
        CS.point_image(file=Path("petrol.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['petrol'] = petrol

    cinema = CTI("point")
    cinema[0:5] = [
        CS.point_image(file=Path("cinema.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['cinema'] = cinema

    bank = CTI("point")
    bank[0:5] = [
        CS.point_image(file=Path("bank.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['bank'] = bank

    gym = CTI("point")
    gym[0:5] = [
        CS.point_image(file=Path("gym.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['gym'] = gym

    shelter = CTI("point")
    shelter[0:5] = [
        CS.point_image(file=Path("shelter.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['shelter'] = shelter

    playground = CTI("point")
    playground[0:5] = [
        CS.point_image(file=Path("playground.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['playground'] = playground

    fountain = CTI("point")
    fountain[0:5] = [
        CS.point_image(file=Path("fountain.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['fountain'] = fountain

    taxi_stand = CTI("point")
    taxi_stand[0:5] = [
        CS.point_image(file=Path("taxistand.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['taxiStand'] = taxi_stand

    pick_up_drop_off = CTI("point")
    pick_up_drop_off[0:5] = [
        CS.point_image(file=Path("pickupdropoff.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['pickUpDropOff'] = pick_up_drop_off"""

    bus_stop = CTI("point")
    for i, sq_size, text_size in ((0, 10, 12), (1, 10, 12)):
        bus_stop[i] = [
            CS.point_square(colour=0x00AAFF, size=sq_size, width=int(2 / 3 * sq_size)),
            CS.point_text(colour=0x00AAFF, offset=(0, 20), size=text_size, anchor="mm"),
        ]
    bus_stop[2:3] = [
        CS.point_square(colour=0x66CCFF, size=7, width=5),
    ]
    s["busStop"] = bus_stop

    ferry_stop = CTI("point")
    for i, sq_size, text_size in ((0, 10, 12), (1, 10, 12)):
        ferry_stop[i] = [
            CS.point_square(colour=0x1E85AE, size=sq_size, width=int(2 / 3 * sq_size)),
            CS.point_text(colour=0x1E85AE, offset=(0, 20), size=text_size, anchor="mm"),
        ]
    ferry_stop[2:3] = [
        CS.point_square(colour=0x1E85AE, size=7, width=5),
    ]
    s["ferryStop"] = ferry_stop

    rail_station = CTI("point")
    for i, sq_size, text_size in ((0, 15, 15), (1, 15, 15), (2, 10, 13)):
        rail_station[i] = [
            CS.point_square(colour=0x1F3D7A, size=sq_size, width=int(2 / 3 * sq_size)),
            CS.point_text(colour=0x1F3D7A, offset=(0, 20), size=text_size, anchor="mm"),
        ]
    rail_station[3:4] = [
        CS.point_square(colour=0x1F3D7A, size=10, width=7),
    ]
    s["railStation"] = rail_station

    """transport_exit = CTI("point")
    transport_exit[0:5] = [
        CS.point_image(file=Path("transportexit.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm"
    ]
    s['transportExit'] = transport_exit

    attraction = CTI("point")
    attraction[0:5] = [
        CS.point_image(file=Path("attraction.png")),
        CS.point_text(colour=0x000000,
                      offset=(0, 32),
                      size=32,
                      anchor="mm"
    ]
    s['attraction'] = attraction"""

    subdistrict = CTI("area")
    subdistrict[0:1] = [
        CS.area_fill(outline=0xD9B38C),
        CS.area_bordertext(colour=0xD9B38C, offset=10, size=20),
    ]
    subdistrict[2:5] = [
        CS.area_fill(outline=0xD9B38C),
        CS.area_bordertext(colour=0xD9B38C, offset=10, size=20),
        CS.area_centertext(colour=0xD9B38C, size=25),
    ]
    s["subdistrict"] = subdistrict

    subdistrict_marker = CTI("point")
    subdistrict_marker[2:5] = [CS.point_text(colour=0xD9B38C, size=25)]
    s["subdistrictMarker"] = subdistrict_marker

    district = CTI("area")
    district[0:3] = [
        CS.area_fill(outline=0xCC9966),
        CS.area_bordertext(colour=0xCC9966, offset=10, size=20),
    ]
    district[4:6] = [
        CS.area_fill(outline=0xCC9966),
        CS.area_bordertext(colour=0xCC9966, offset=10, size=20),
        CS.area_centertext(colour=0xCC9966, size=25),
    ]
    s["district"] = district

    district_marker = CTI("point")
    district_marker[4:6] = [CS.point_text(colour=0xCC9966, size=25)]
    s["districtMarker"] = district_marker

    town = CTI("area")
    town[0:3] = [
        CS.area_fill(outline=0xBF8040),
        CS.area_bordertext(colour=0xBF8040, offset=10, size=20),
    ]
    town[4:8] = [
        CS.area_fill(outline=0xBF8040),
        CS.area_bordertext(colour=0xBF8040, offset=10, size=20),
        CS.area_centertext(colour=0xBF8040, size=25),
    ]
    town[9:11] = [
        CS.area_fill(outline=0xBF8040),
        CS.area_centertext(colour=0xBF8040, size=25),
    ]
    s["town"] = town

    town_marker = CTI("point")
    town_marker[4:8] = [
        CS.point_circle(colour=0xDDDDDD, outline=0x000000, size=5, width=2),
        CS.point_text(colour=0xBF8040, size=25),
    ]
    s["townMarker"] = town_marker

    state = CTI("area")
    state[0:4] = [
        CS.area_fill(outline=0x996633),
        CS.area_bordertext(colour=0x996633, offset=10, size=20),
    ]
    state[5:10] = [
        CS.area_fill(outline=0x996633),
        CS.area_bordertext(colour=0x996633, offset=10, size=20),
        CS.area_centertext(colour=0x996633, size=25),
    ]
    state[11:13] = [
        CS.area_fill(outline=0x996633),
        CS.area_centertext(colour=0x996633, size=25),
    ]
    s["state"] = state

    state_marker = CTI("point")
    state_marker[5:10] = [CS.point_text(colour=0x996633, size=25)]
    s["stateMarker"] = state_marker

    country = CTI("area")
    country[0:4] = [
        CS.area_fill(outline=0x86592D),
        CS.area_bordertext(colour=0x86592D, offset=10, size=20),
    ]
    country[5:10] = [
        CS.area_fill(outline=0x86592D),
        CS.area_bordertext(colour=0x86592D, offset=10, size=20),
        CS.area_centertext(colour=0x86592D, size=25),
    ]
    country[11:13] = [
        CS.area_fill(outline=0x86592D),
        CS.area_centertext(colour=0x86592D, size=25),
    ]
    s["country"] = country

    country_marker = CTI("point")
    country_marker[5:10] = [CS.point_text(colour=0x86592D, size=25)]
    s["countryMarker"] = country_marker

    # TODO ward

    simple_area = CTI("area")
    simple_area[0:5] = [
        CS.area_fill(colour=0xAAAAAA, outline=0x808080, stripe=(10, 10, 45)),
        CS.area_bordertext(colour=0x555555, offset=10, size=20),
        CS.area_centertext(colour=0x555555, size=50),
    ]
    s["simpleArea"] = simple_area

    simple_line = CTI("line")
    simple_line[0:5] = [CS.line_fore(colour=0x808080, width=8)]
    s["simpleLine"] = simple_line

    simple_point = CTI("point")
    simple_point[0:5] = [
        CS.point_circle(colour=0xFFFFFF, outline=0x000000, size=30, width=6),
        CS.point_text(colour=0x000000, offset=(10, 10), size=25),
    ]
    s["simplePoint"] = simple_point

    with Path("default.json").open("w") as f:
        json.dump(s.json(), f, indent=2)


if __name__ == "__main__":
    main()
