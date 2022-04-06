import json
from pathlib import Path

from renderer.objects.skinbuilder import SkinBuilder, CTI, CS, _darken, _lighten
from renderer.types import Coord

A_ROAD = 0xffaaaa
B_ROAD = 0xff8000
LOCAL_HIGHWAY = 0xffcc80
LOCAL_MAIN = 0xffee00
LOCAL_SECONDARY = 0xfff899
LOCAL_TERTIARY_QUATERNARY = 0xeeeeee
LOCAL_PEDESTRIAN = 0xccccff
BUILDING = 0xa2a288
TRANSPORT_BUILDING = 0x999966

def main():
    s = SkinBuilder(256, {
        "": Path("ClearSans-Medium.ttf"),
        "b": Path("ClearSans-Bold.ttf"),
        "i": Path("ClearSans-MediumItalic.ttf"),
        "bi": Path("ClearSans-BoldItalic.ttf")
    }, 0xdddddd)

    residential_area = CTI("area")
    residential_area[0:5] = [
        CS.area_fill(colour=0xb3cbcb),
        CS.area_centertext(colour=_darken(0xb3cbcb),
                           size=30)
    ]
    s['residentialArea'] = residential_area

    industrial_area = CTI("area")
    industrial_area[0:5] = [
        CS.area_fill(colour=0xffccb3),
        CS.area_centertext(colour=_darken(0xffccb3),
                           size=30)
    ]
    s['industrialArea'] = industrial_area

    commercial_area = CTI("area")
    commercial_area[0:5] = [
        CS.area_fill(colour=0xe7b1ca),
        CS.area_centertext(colour=_darken(0xe7b1ca),
                           size=30)
    ]
    s['commercialArea'] = commercial_area

    office_area = CTI("area")
    office_area[0:5] = [
        CS.area_fill(colour=0xffcc99),
        CS.area_centertext(colour=_darken(0xffcc99),
                           size=30)
    ]
    s['officeArea'] = office_area

    residential_office_area = CTI("area")
    residential_office_area[0:5] = [
        CS.area_fill(colour=0xd9dbb2),
        CS.area_centertext(colour=_darken(0xd9dbb2),
                           size=30)
    ]
    s['residentialOfficeArea'] = residential_office_area

    school_area = CTI("area")
    school_area[0:5] = [
        CS.area_fill(colour=0xecc6c6),
        CS.area_centertext(colour=_darken(0xecc6c6),
                           size=30)
    ]
    s['schoolArea'] = school_area

    health_area = CTI("area")
    health_area[0:5] = [
        CS.area_fill(colour=0xff9999),
        CS.area_centertext(colour=_darken(0xff9999),
                           size=30)
    ]
    s['healthArea'] = health_area

    agriculture_area = CTI("area")
    agriculture_area[0:5] = [
        CS.area_fill(colour=0xccff99),
        CS.area_centertext(colour=_darken(0xccff99),
                           size=30)
    ]
    s['agricultureArea'] = agriculture_area

    military_area = CTI("area")
    military_area[0:5] = [
        CS.area_fill(colour=0xc2c2a3),
        CS.area_centertext(colour=_darken(0xc2c2a3),
                           size=30)
    ]
    s['militaryArea'] = military_area

    water_large = CTI("area")
    water_large[0:] = [
        CS.area_fill(colour=0x87ceeb),
        CS.area_centertext(colour=_darken(0x87ceeb),
                           size=50)
    ]
    s['waterLarge'] = water_large

    water_small = CTI("area")
    water_small[0:2] = [
        CS.area_fill(colour=0x87ceeb),
        CS.area_centertext(colour=_darken(0x87ceeb),
                           size=25)
    ]
    water_small[3:5] = [
        CS.area_fill(colour=0x87ceeb)
    ]
    s['waterSmall'] = water_small

    land_large = CTI("area")
    land_large[0:] = [
        CS.area_fill(colour=0xdddddd),
        CS.area_centertext(colour=0x808080,
                           size=50)
    ]
    s['landLarge'] = land_large

    land_small = CTI("area")
    land_small[0:2] = [
        CS.area_fill(colour=0xdddddd),
        CS.area_centertext(colour=0x808080,
                           size=50)
    ]
    land_small[3:5] = [
        CS.area_fill(colour=0xdddddd)
    ]
    s['landSmall'] = land_small

    waterway = CTI("line")
    waterway[0:5] = [
        CS.line_fore(colour=0x87ceeb,
                     width=10),
        CS.line_text(colour=_darken(0x87ceeb),
                     arrow_colour=_darken(0x87ceeb, 0.25),
                     size=20)
    ]
    s['waterway'] = waterway

    ferry_line = CTI("line")
    ferry_line[0:5] = [
        CS.line_fore(colour=0x25a7da,
                     width=10),
        CS.line_text(colour=_darken(0x25a7da),
                     arrow_colour=0x25a7da,
                     size=10)
    ]
    s['ferryLine'] = ferry_line

    grass = CTI("area")
    grass[0:5] = [
        CS.area_fill(colour=0xbbff99),
        CS.area_centertext(colour=_darken(0xbbff99),
                           size=25)
    ]
    s['grass'] = grass

    shrub = CTI("area")
    shrub[0:5] = [
        CS.area_fill(colour=0x99ff99),
        CS.area_centertext(colour=_darken(0x99ff99),
                           size=25)
    ]
    s['shrub'] = shrub

    forest = CTI("area")
    forest[0:5] = [
        CS.area_fill(colour=0x5ca904),
        CS.area_centertext(colour=_darken(0x5ca904),
                           size=25)
    ]
    s['forest'] = forest

    stone = CTI("area")
    stone[0:5] = [
        CS.area_fill(colour=0xaaaaaa),
        CS.area_centertext(colour=_darken(0xaaaaaa),
                           size=25)
    ]
    s['stone'] = stone

    sand = CTI("area")
    sand[0:5] = [
        CS.area_fill(colour=0xf7e1a1),
        CS.area_centertext(colour=_darken(0xf7e1a1),
                           size=25)
    ]
    s['sand'] = sand

    gate = CTI("area")
    gate[0:5] = [
        CS.area_fill(outline=0x33334d),
        CS.area_centertext(colour=0x33334d,
                           size=15)
    ]
    s['gate'] = gate

    apron = CTI("area")
    apron[0:5] = [
        CS.area_fill(colour=0xc2c2d6),
        CS.area_centertext(colour=0x33334d,
                           size=30)
    ]
    s['apron'] = apron

    taxiway = CTI("line")
    taxiway[0:2] = [
        CS.line_fore(colour=0x8f8fa3,
                     width=50),
        CS.line_text(colour=0x33334d,
                     arrow_colour=0x8f8fa3,
                     size=20)
    ]
    taxiway[3:5] = [
        CS.line_fore(colour=0x8f8fa3,
                     width=25),
        CS.line_text(colour=0x33334d,
                     arrow_colour=0x8f8fa3,
                     size=10)
    ]
    s['taxiway'] = taxiway

    runway = CTI("line", ["unroundedEnds"])
    runway[0:2] = [
        CS.line_fore(colour=0x73738c,
                     width=100),
        CS.line_text(colour=0x33334d,
                     arrow_colour=0x73738c,
                     size=30)
    ]
    runway[3:5] = [
        CS.line_fore(colour=0x73738c,
                     width=50),
        CS.line_text(colour=0x33334d,
                     arrow_colour=0x73738c,
                     size=15)
    ]
    s['runway'] = runway

    helipad = CTI("area")
    helipad[0:5] = [
        CS.area_fill(colour=0xff99ff,
                     outline=0xff66ff),
        CS.area_centertext(colour=0xff66ff,
                           size=50)
    ]
    s['helipad'] = helipad

    plaza = CTI("area")
    plaza[0:5] = [
        CS.area_fill(colour=0xccccff,
                     outline=0xbbbbbb),
        CS.area_centertext(colour=0x000000,
                           size=15)
    ]
    s['plaza'] = plaza

    building_underground = CTI("area")
    building_underground[0:5] = [
        CS.area_fill(colour=_lighten(BUILDING),
                     outline=BUILDING),
        CS.area_centertext(colour=_darken(BUILDING),
                           size=15)
    ]
    s['building_underground'] = building_underground

    # TODO cityHall_underground

    transport_building_underground = CTI("area")
    transport_building_underground[0:5] = [
        CS.area_fill(colour=_lighten(TRANSPORT_BUILDING),
                     outline=TRANSPORT_BUILDING),
        CS.area_centertext(colour=_darken(TRANSPORT_BUILDING),
                           size=30)
    ]
    s['transportBuilding_underground'] = transport_building_underground

    platform_underground = CTI("area")
    platform_underground[0:5] = [
        CS.area_fill(colour=0xaaaaaa,
                     outline=_darken(0xaaaaaa)),
        CS.area_centertext(colour=_darken(0xaaaaaa),
                           size=10)
    ]
    s['platform_underground'] = platform_underground

    park = CTI("area")
    park[0:5] = [
        CS.area_fill(colour=0x669900),
        CS.area_centertext(colour=_darken(0x669900),
                           size=25)
    ]
    s['park'] = park

    pathway_underground = CTI("line", ["road"])
    pathway_underground[0:5] = [
        CS.line_back(colour=0xeeeeee,
                     width=8),
        CS.line_fore(colour=0x66ff66,
                     width=4,
                     dash=(16, 16)),
        CS.line_text(colour=0xaaaaaa,
                     arrow_colour=0xeeeeee,
                     size=16,
                     offset=10)
    ]
    s['pathway_underground'] = pathway_underground

    local_highway_slip_underground = CTI("line", ["road"])
    local_highway_slip_underground[0:5] = [
        CS.line_back(colour=LOCAL_HIGHWAY,
                     width=28),
        CS.line_fore(colour=_lighten(LOCAL_HIGHWAY),
                     width=20),
        CS.line_text(colour=0x000000,
                     arrow_colour=LOCAL_HIGHWAY,
                     size=20)
    ]
    s['localHighwaySlip_underground'] = local_highway_slip_underground

    b_road_slip_underground = CTI("line", ["road"])
    b_road_slip_underground[0:5] = [
        CS.line_back(colour=B_ROAD,
                     width=32),
        CS.line_fore(colour=_lighten(B_ROAD),
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=B_ROAD,
                     size=24)
    ]
    s['bRoadSlip_underground'] = b_road_slip_underground

    a_road_slip_underground = CTI("line", ["road"])
    a_road_slip_underground[0:5] = [
        CS.line_back(colour=A_ROAD,
                     width=40),
        CS.line_fore(colour=_lighten(A_ROAD),
                     width=32),
        CS.line_text(colour=A_ROAD,
                     arrow_colour=0xffb3b3,
                     size=32)
    ]
    s['aRoadSlip_underground'] = a_road_slip_underground

    local_pedestrian_quaternary_road_underground = CTI("line", ["road"])
    local_pedestrian_quaternary_road_underground[0:5] = [
        CS.line_back(colour=LOCAL_PEDESTRIAN,
                     width=24),
        CS.line_fore(colour=_lighten(LOCAL_PEDESTRIAN),
                     width=16),
        CS.line_text(colour=0x000000,
                     arrow_colour=LOCAL_PEDESTRIAN,
                     size=16)
    ]
    s['localPedestrianQuaternaryRoad_underground'] = local_pedestrian_quaternary_road_underground

    local_quaternary_road_underground = CTI("line", ["road"])
    local_quaternary_road_underground[0:5] = [
        CS.line_back(colour=LOCAL_TERTIARY_QUATERNARY,
                     width=24),
        CS.line_fore(colour=_lighten(LOCAL_TERTIARY_QUATERNARY),
                     width=16),
        CS.line_text(colour=LOCAL_TERTIARY_QUATERNARY,
                     arrow_colour=0xb3b3b3,
                     size=16)
    ]
    s['localQuaternaryRoad_underground'] = local_quaternary_road_underground

    local_pedestrian_tertiary_road_underground = CTI("line", ["road"])
    local_pedestrian_tertiary_road_underground[0:5] = [
        CS.line_back(colour=LOCAL_PEDESTRIAN,
                     width=32),
        CS.line_fore(colour=_lighten(LOCAL_PEDESTRIAN),
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=LOCAL_PEDESTRIAN,
                     size=24)
    ]
    s['localPedestrianTertiaryRoad_underground'] = local_pedestrian_tertiary_road_underground

    local_tertiary_road_underground = CTI("line", ["road"])
    local_tertiary_road_underground[0:5] = [
        CS.line_back(colour=LOCAL_TERTIARY_QUATERNARY,
                     width=32),
        CS.line_fore(colour=_lighten(LOCAL_TERTIARY_QUATERNARY),
                     width=24),
        CS.line_text(colour=LOCAL_TERTIARY_QUATERNARY,
                     arrow_colour=0xb3b3b3,
                     size=24)
    ]
    s['localTertiaryRoad_underground'] = local_tertiary_road_underground

    local_secondary_road_underground = CTI("line", ["road"])
    local_secondary_road_underground[0:5] = [
        CS.line_back(colour=LOCAL_SECONDARY,
                     width=36),
        CS.line_fore(colour=_lighten(LOCAL_SECONDARY),
                     width=28),
        CS.line_text(colour=0x000000,
                     arrow_colour=LOCAL_SECONDARY,
                     size=28)
    ]
    s['localSecondaryRoad_underground'] = local_secondary_road_underground

    local_main_road_underground = CTI("line", ["road"])
    local_main_road_underground[0:5] = [
        CS.line_back(colour=LOCAL_MAIN,
                     width=40),
        CS.line_fore(colour=_lighten(LOCAL_MAIN),
                     width=32),
        CS.line_text(colour=0x000000,
                     arrow_colour=LOCAL_MAIN,
                     size=32)
    ]
    s['localMainRoad_underground'] = local_main_road_underground

    local_highway_underground = CTI("line", ["road"])
    local_highway_underground[0:5] = [
        CS.line_back(colour=LOCAL_HIGHWAY,
                     width=44),
        CS.line_fore(colour=_lighten(LOCAL_HIGHWAY),
                     width=36),
        CS.line_text(colour=0x000000,
                     arrow_colour=LOCAL_HIGHWAY,
                     size=36)
    ]
    s['localHighway_underground'] = local_highway_underground

    b_road_underground = CTI("line", ["road"])
    b_road_underground[0:5] = [
        CS.line_back(colour=B_ROAD,
                     width=48),
        CS.line_fore(colour=_lighten(B_ROAD),
                     width=40),
        CS.line_text(colour=0x000000,
                     arrow_colour=B_ROAD,
                     size=40)
    ]
    s['bRoad_underground'] = b_road_underground

    a_road_underground = CTI("line", ["road"])
    a_road_underground[0:5] = [
        CS.line_back(colour=A_ROAD,
                     width=56),
        CS.line_fore(colour=_lighten(A_ROAD),
                     width=48),
        CS.line_text(colour=0x000000,
                     arrow_colour=A_ROAD,
                     size=48)
    ]
    s['aRoad_underground'] = a_road_underground

    rail_underground = CTI("line", ["road"])
    rail_underground[0:5] = [
        CS.line_fore(colour=0x808080,
                     width=8,
                     dash=(50, 25)),
        CS.line_text(colour=0x808080,
                     arrow_colour=0x808080,
                     offset=16,
                     size=16)
    ]
    s['rail_underground'] = rail_underground

    # TODO intercityRail_underground

    building = CTI("area")
    building[0:5] = [
        CS.area_fill(colour=BUILDING,
                     outline=_darken(BUILDING)),
        CS.area_centertext(colour=_darken(BUILDING),
                           size=15)
    ]
    s['building'] = building

    city_hall = CTI("area")
    city_hall[0:5] = [
        CS.area_fill(colour=0xffaaaa,
                     outline=_darken(0xffaaaa)),
        CS.area_centertext(colour=_darken(0xffaaaa),
                           size=30)
    ]
    s['cityHall'] = city_hall

    transport_building = CTI("area")
    transport_building[0:5] = [
        CS.area_fill(colour=TRANSPORT_BUILDING,
                     outline=_darken(TRANSPORT_BUILDING)),
        CS.area_centertext(colour=_darken(TRANSPORT_BUILDING),
                           size=30)
    ]
    s['transportBuilding'] = transport_building

    platform = CTI("area")
    platform[0:5] = [
        CS.area_fill(colour=0xcccccc,
                     outline=0x808080),
        CS.area_centertext(colour=0x808080,
                           size=10)
    ]
    s['platform'] = platform

    pathway = CTI("line", ["road"])
    pathway[0:5] = [
        CS.line_back(colour=0xeeeeee,
                     width=8),
        CS.line_fore(colour=0x008000,
                     width=4,
                     dash=(16, 16)),
        CS.line_text(colour=0xaaaaaa,
                     arrow_colour=0xeeeeee,
                     size=16,
                     offset=10)
    ]
    s['pathway'] = pathway

    local_highway_slip = CTI("line", ["road"])
    local_highway_slip[0:5] = [
        CS.line_back(colour=_darken(LOCAL_HIGHWAY, 0.25),
                     width=28),
        CS.line_fore(colour=LOCAL_HIGHWAY,
                     width=20),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_HIGHWAY, 0.25),
                     size=20)
    ]
    s['localHighwaySlip'] = local_highway_slip

    b_road_slip = CTI("line", ["road"])
    b_road_slip[0:5] = [
        CS.line_back(colour=_darken(B_ROAD, 0.25),
                     width=32),
        CS.line_fore(colour=B_ROAD,
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(B_ROAD, 0.25),
                     size=24)
    ]
    s['bRoadSlip'] = b_road_slip

    a_road_slip = CTI("line", ["road"])
    a_road_slip[0:5] = [
        CS.line_back(colour=_darken(A_ROAD, 0.25),
                     width=40),
        CS.line_fore(colour=A_ROAD,
                     width=32),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(A_ROAD, 0.25),
                     size=32)
    ]
    s['aRoadSlip'] = a_road_slip

    local_pedestrian_quaternary_road = CTI("line", ["road"])
    local_pedestrian_quaternary_road[0:5] = [
        CS.line_back(colour=_darken(LOCAL_PEDESTRIAN, 0.25),
                     width=24),
        CS.line_fore(colour=LOCAL_PEDESTRIAN,
                     width=16),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_PEDESTRIAN, 0.25),
                     size=16)
    ]
    s['localPedestrianQuaternaryRoad'] = local_pedestrian_quaternary_road

    local_quaternary_road = CTI("line", ["road"])
    local_quaternary_road[0:5] = [
        CS.line_back(colour=_darken(LOCAL_TERTIARY_QUATERNARY, 0.25),
                     width=24),
        CS.line_fore(colour=LOCAL_TERTIARY_QUATERNARY,
                     width=16),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_TERTIARY_QUATERNARY, 0.25),
                     size=16)
    ]
    s['localQuaternaryRoad'] = local_quaternary_road

    local_pedestrian_tertiary_road = CTI("line", ["road"])
    local_pedestrian_tertiary_road[0:5] = [
        CS.line_back(colour=_darken(LOCAL_PEDESTRIAN, 0.25),
                     width=32),
        CS.line_fore(colour=LOCAL_PEDESTRIAN,
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_PEDESTRIAN, 0.25),
                     size=24)
    ]
    s['localPedestrianTertiaryRoad'] = local_pedestrian_tertiary_road

    local_tertiary_road = CTI("line", ["road"])
    local_tertiary_road[0:5] = [
        CS.line_back(colour=_darken(LOCAL_TERTIARY_QUATERNARY, 0.25),
                     width=32),
        CS.line_fore(colour=LOCAL_TERTIARY_QUATERNARY,
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_TERTIARY_QUATERNARY, 0.25),
                     size=24)
    ]
    s['localTertiaryRoad'] = local_tertiary_road

    local_secondary_road = CTI("line", ["road"])
    local_secondary_road[0:5] = [
        CS.line_back(colour=_darken(LOCAL_SECONDARY, 0.25),
                     width=36),
        CS.line_fore(colour=LOCAL_SECONDARY,
                     width=28),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_SECONDARY, 0.25),
                     size=28)
    ]
    s['localSecondaryRoad'] = local_secondary_road

    local_main_road = CTI("line", ["road"])
    local_main_road[0:5] = [
        CS.line_back(colour=_darken(LOCAL_MAIN, 0.25),
                     width=40),
        CS.line_fore(colour=LOCAL_MAIN,
                     width=32),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_MAIN, 0.25),
                     size=32)
    ]
    s['localMainRoad'] = local_main_road

    local_highway = CTI("line", ["road"])
    local_highway[0:5] = [
        CS.line_back(colour=_darken(LOCAL_HIGHWAY, 0.25),
                     width=44),
        CS.line_fore(colour=LOCAL_HIGHWAY,
                     width=36),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_HIGHWAY, 0.25),
                     size=36)
    ]
    s['localHighway'] = local_highway

    b_road = CTI("line", ["road"])
    b_road[0:5] = [
        CS.line_back(colour=_darken(B_ROAD, 0.25),
                     width=48),
        CS.line_fore(colour=B_ROAD,
                     width=40),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(B_ROAD, 0.25),
                     size=40)
    ]
    s['bRoad'] = b_road

    a_road = CTI("line", ["road"])
    a_road[0:5] = [
        CS.line_back(colour=_darken(A_ROAD, 0.25),
                     width=56),
        CS.line_fore(colour=A_ROAD,
                     width=48),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(A_ROAD, 0.25),
                     size=48)
    ]
    s['aRoad'] = a_road

    rail = CTI("line", ["road"])
    rail[0:5] = [
        CS.line_fore(colour=0x808080,
                     width=8),
        CS.line_text(colour=0x808080,
                     arrow_colour=0x808080,
                     offset=16,
                     size=16)
    ]
    s['rail'] = rail

    # TODO intercityRail

    pathway_elevated = CTI("line", ["road"])
    pathway_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=12),
        CS.line_back(colour=0xeeeeee,
                     width=8),
        CS.line_fore(colour=0x008000,
                     width=4,
                     dash=(16, 16)),
        CS.line_text(colour=0xaaaaaa,
                     arrow_colour=0x008000,
                     size=16,
                     offset=10)
    ]
    s['pathway_elevated'] = pathway_elevated

    local_highway_slip_elevated = CTI("line", ["road"])
    local_highway_slip_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=28),
        CS.line_fore(colour=LOCAL_HIGHWAY,
                     width=20),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_HIGHWAY, 0.25),
                     size=20)
    ]
    s['localHighwaySlip_elevated'] = local_highway_slip_elevated

    b_road_slip_elevated = CTI("line", ["road"])
    b_road_slip_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=32),
        CS.line_fore(colour=B_ROAD,
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(B_ROAD, 0.25),
                     size=24)
    ]
    s['bRoadSlip_elevated'] = b_road_slip_elevated

    a_road_slip_elevated = CTI("line", ["road"])
    a_road_slip_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=40),
        CS.line_fore(colour=A_ROAD,
                     width=32),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(A_ROAD, 0.25),
                     size=32)
    ]
    s['aRoadSlip_elevated'] = a_road_slip_elevated

    local_pedestrian_quaternary_road_elevated = CTI("line", ["road"])
    local_pedestrian_quaternary_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=24),
        CS.line_fore(colour=LOCAL_PEDESTRIAN,
                     width=16),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_PEDESTRIAN, 0.25),
                     size=16)
    ]
    s['localPedestrianQuaternaryRoad_elevated'] = local_pedestrian_quaternary_road_elevated

    local_quaternary_road_elevated = CTI("line", ["road"])
    local_quaternary_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=24),
        CS.line_fore(colour=LOCAL_TERTIARY_QUATERNARY,
                     width=16),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_TERTIARY_QUATERNARY, 0.25),
                     size=16)
    ]
    s['localQuaternaryRoad_elevated'] = local_quaternary_road_elevated

    local_pedestrian_tertiary_road_elevated = CTI("line", ["road"])
    local_pedestrian_tertiary_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=32),
        CS.line_fore(colour=LOCAL_PEDESTRIAN,
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_PEDESTRIAN, 0.25),
                     size=24)
    ]
    s['localPedestrianTertiaryRoad_elevated'] = local_pedestrian_tertiary_road_elevated

    local_tertiary_road_elevated = CTI("line", ["road"])
    local_tertiary_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=32),
        CS.line_fore(colour=LOCAL_TERTIARY_QUATERNARY,
                     width=24),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_TERTIARY_QUATERNARY, 0.25),
                     size=24)
    ]
    s['localTertiaryRoad_elevated'] = local_tertiary_road_elevated

    local_secondary_road_elevated = CTI("line", ["road"])
    local_secondary_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=36),
        CS.line_fore(colour=LOCAL_SECONDARY,
                     width=28),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_SECONDARY, 0.25),
                     size=28)
    ]
    s['localSecondaryRoad_elevated'] = local_secondary_road_elevated

    local_main_road_elevated = CTI("line", ["road"])
    local_main_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=40),
        CS.line_fore(colour=LOCAL_MAIN,
                     width=32),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_MAIN, 0.25),
                     size=32)
    ]
    s['localMainRoad_elevated'] = local_main_road_elevated

    local_highway_elevated = CTI("line", ["road"])
    local_highway_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=44),
        CS.line_fore(colour=LOCAL_HIGHWAY,
                     width=36),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(LOCAL_HIGHWAY, 0.25),
                     size=36)
    ]
    s['localHighway_elevated'] = local_highway_elevated

    b_road_elevated = CTI("line", ["road"])
    b_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=48),
        CS.line_fore(colour=B_ROAD,
                     width=40),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(B_ROAD, 0.25),
                     size=40)
    ]
    s['bRoad_elevated'] = b_road_elevated

    a_road_elevated = CTI("line", ["road"])
    a_road_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=56),
        CS.line_fore(colour=A_ROAD,
                     width=48),
        CS.line_text(colour=0x000000,
                     arrow_colour=_darken(A_ROAD, 0.25),
                     size=48)
    ]
    s['aRoad_elevated'] = a_road_elevated

    rail_elevated = CTI("line", ["road"])
    rail_elevated[0:5] = [
        CS.line_back(colour=0x000000,
                     width=16),
        CS.line_fore(colour=0x808080,
                     width=8),
        CS.line_text(colour=0x808080,
                     arrow_colour=0x808080,
                     offset=16,
                     size=16)
    ]
    s['rail_elevated'] = rail_elevated

    # TODO intercityRail_elevated

    pedestrian_crossing = CTI("point")
    pedestrian_crossing[0:5] = [
        CS.point_image(file=Path("pedestriancrossing.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['pedestrianCrossing'] = pedestrian_crossing

    rail_crossing = CTI("point")
    rail_crossing[0:5] = [
        CS.point_image(file=Path("pedestriancrossing.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['railCrossing'] = rail_crossing

    parking = CTI("point")
    parking[0:5] = [
        CS.point_image(file=Path("parking.png")),
        CS.point_text(colour=0x0000dc,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['parking'] = parking

    bike_rack = CTI("point")
    bike_rack[0:5] = [
        CS.point_image(file=Path("bikerack.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['bikeRack'] = bike_rack

    shop = CTI("point")
    shop[0:5] = [
        CS.point_image(file=Path("shop.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['shop'] = shop

    restaurant = CTI("point")
    restaurant[0:5] = [
        CS.point_image(file=Path("restaurant.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['restaurant'] = restaurant

    hotel = CTI("point")
    hotel[0:5] = [
        CS.point_image(file=Path("hotel.png")),
        CS.point_text(colour=0x0000fc,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['hotel'] = hotel

    arcade = CTI("point")
    arcade[0:5] = [
        CS.point_image(file=Path("arcade.png")),
        CS.point_text(colour=0xffdc00,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['arcade'] = arcade

    supermarket = CTI("point")
    supermarket[0:5] = [
        CS.point_image(file=Path("supermarket.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['supermarket'] = supermarket

    clinic = CTI("point")
    clinic[0:5] = [
        CS.point_image(file=Path("clinic.png")),
        CS.point_text(colour=0xff0303,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['clinic'] = clinic

    '''library = CTI("point")
    library[0:5] = [
        CS.point_image(file=Path("library.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['library'] = library

    place_of_worship = CTI("point")
    place_of_worship[0:5] = [
        CS.point_image(file=Path("placeofworship.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['placeOfWorship'] = place_of_worship

    petrol = CTI("point")
    petrol[0:5] = [
        CS.point_image(file=Path("petrol.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['petrol'] = petrol

    cinema = CTI("point")
    cinema[0:5] = [
        CS.point_image(file=Path("cinema.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['cinema'] = cinema

    bank = CTI("point")
    bank[0:5] = [
        CS.point_image(file=Path("bank.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['bank'] = bank

    gym = CTI("point")
    gym[0:5] = [
        CS.point_image(file=Path("gym.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['gym'] = gym

    shelter = CTI("point")
    shelter[0:5] = [
        CS.point_image(file=Path("shelter.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['shelter'] = shelter

    playground = CTI("point")
    playground[0:5] = [
        CS.point_image(file=Path("playground.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['playground'] = playground

    fountain = CTI("point")
    fountain[0:5] = [
        CS.point_image(file=Path("fountain.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['fountain'] = fountain

    taxi_stand = CTI("point")
    taxi_stand[0:5] = [
        CS.point_image(file=Path("taxistand.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['taxiStand'] = taxi_stand

    pick_up_drop_off = CTI("point")
    pick_up_drop_off[0:5] = [
        CS.point_image(file=Path("pickupdropoff.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm")
    ]
    s['pickUpDropOff'] = pick_up_drop_off'''

    bus_stop = CTI("point")
    bus_stop[0:5] = [
        CS.point_square(colour=0x66ccff,
                        size=15,
                        width=10),
        CS.point_text(colour=0x66ccff,
                      offset=Coord(0, 20),
                      size=15,
                      anchor="mm")
    ]
    s['busStop'] = bus_stop

    ferry_stop = CTI("point")
    ferry_stop[0:5] = [
        CS.point_square(colour=0x1e85ae,
                        size=15,
                        width=10),
        CS.point_text(colour=0x1e85ae,
                      offset=Coord(0, 20),
                      size=15,
                      anchor="mm")
    ]
    s['ferryStop'] = ferry_stop

    rail_station = CTI("point")
    rail_station[0:5] = [
        CS.point_square(colour=0x1f3d7a,
                        size=15,
                        width=10),
        CS.point_text(colour=0x1f3d7a,
                      offset=Coord(0, 20),
                      size=15,
                      anchor="mm")
    ]
    s['railStation'] = rail_station

    '''transport_exit = CTI("point")
    transport_exit[0:5] = [
        CS.point_image(file=Path("transportexit.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm"
    ]
    s['transportExit'] = transport_exit

    attraction = CTI("point")
    attraction[0:5] = [
        CS.point_image(file=Path("attraction.png")),
        CS.point_text(colour=0x000000,
                      offset=Coord(0, 32),
                      size=32,
                      anchor="mm"
    ]
    s['attraction'] = attraction'''

    subdistrict = CTI("area")
    subdistrict[0:1] = [
        CS.area_fill(outline=0xd9b38c),
        CS.area_bordertext(colour=0xd9b38c,
                           offset=10,
                           size=20)
    ]
    subdistrict[2:5] = [
        CS.area_fill(outline=0xd9b38c),
        CS.area_bordertext(colour=0xd9b38c,
                           offset=10,
                           size=20),
        CS.area_centertext(colour=0xd9b38c,
                           size=50)
    ]
    s['subdistrict'] = subdistrict

    district = CTI("area")
    district[0:3] = [
        CS.area_fill(outline=0xcc9966),
        CS.area_bordertext(colour=0xcc9966,
                           offset=10,
                           size=20)
    ]
    district[4:6] = [
        CS.area_fill(outline=0xcc9966),
        CS.area_bordertext(colour=0xcc9966,
                           offset=10,
                           size=20),
        CS.area_centertext(colour=0xcc9966,
                           size=50)
    ]
    s['district'] = district

    town = CTI("area")
    town[0:3] = [
        CS.area_fill(outline=0xbf8040),
        CS.area_bordertext(colour=0xbf8040,
                           offset=10,
                           size=20)
    ]
    town[4:8] = [
        CS.area_fill(outline=0xbf8040),
        CS.area_bordertext(colour=0xbf8040,
                           offset=10,
                           size=20),
        CS.area_centertext(colour=0xbf8040,
                           size=50)
    ]
    town[9:11] = [
        CS.area_fill(outline=0xbf8040),
        CS.area_centertext(colour=0xbf8040,
                           size=25)
    ]
    s['town'] = town

    state = CTI("area")
    state[0:4] = [
        CS.area_fill(outline=0x996633),
        CS.area_bordertext(colour=0x996633,
                           offset=10,
                           size=20)
    ]
    state[5:10] = [
        CS.area_fill(outline=0x996633),
        CS.area_bordertext(colour=0x996633,
                           offset=10,
                           size=20),
        CS.area_centertext(colour=0x996633,
                           size=50)
    ]
    state[11:13] = [
        CS.area_fill(outline=0x996633),
        CS.area_centertext(colour=0x996633,
                           size=25)
    ]
    s['state'] = state

    country = CTI("area")
    country[0:4] = [
        CS.area_fill(outline=0x86592d),
        CS.area_bordertext(colour=0x86592d,
                           offset=10,
                           size=20)
    ]
    country[5:10] = [
        CS.area_fill(outline=0x86592d),
        CS.area_bordertext(colour=0x86592d,
                           offset=10,
                           size=20),
        CS.area_centertext(colour=0x86592d,
                           size=50)
    ]
    country[11:13] = [
        CS.area_fill(outline=0x86592d),
        CS.area_centertext(colour=0x86592d,
                           size=25)
    ]
    s['country'] = country

    # TODO ward

    simple_area = CTI("area")
    simple_area[0:5] = [
        CS.area_fill(colour=0xaaaaaa,
                     outline=0x808080,
                     stripe=(10, 10, 45)),
        CS.area_bordertext(colour=0x555555,
                           offset=10,
                           size=20),
        CS.area_centertext(colour=0x555555,
                           size=50)
    ]
    s['simpleArea'] = simple_area

    simple_line = CTI("line")
    simple_line[0:5] = [
        CS.line_fore(colour=0x808080,
                     width=8)
    ]
    s['simpleLine'] = simple_line

    simple_point = CTI("point")
    simple_point[0:5] = [
        CS.point_circle(colour=0xffffff,
                        outline=0x000000,
                        size=30,
                        width=6),
        CS.point_text(colour=0x000000,
                      offset=Coord(10, 10),
                      size=25)
    ]
    s['simplePoint'] = simple_point

    with open("default.json", "w") as f:
        json.dump(s.json(), f, indent=2)


if __name__ == '__main__': main()