from pathlib import Path

from renderer.objects.skinbuilder import SkinBuilder, CTI, CS

s = SkinBuilder(256, {
            "": Path("ClearSans-Medium.ttf"),
            "b": Path("ClearSans-Bold.ttf"),
            "i": Path("ClearSans-MediumItalic.ttf"),
            "bi": Path("ClearSans-BoldItalic.ttf")
        }, 0xddd)

residential_area = CTI("area")
residential_area[0:5] = [
    CS.area_fill(colour=0xb3cbcb),
    CS.area_centertext(colour=0x008080,
                       size=30)
]
s['residentialArea'] = residential_area

industrial_area = CTI("area")
industrial_area[0:5] = [
    CS.area_fill(colour=0xffccb3),
    CS.area_centertext(colour=0xc40,
                       size=30)
]
s['industrialArea'] = industrial_area

commercial_area = CTI("area")
commercial_area[0:5] = [
    CS.area_fill(colour=0xe7b1ca),
    CS.area_centertext(colour=0xc33c7b,
                       size=30)
]
s['commercialArea'] = commercial_area

office_area = CTI("area")
office_area[0:5] = [
    CS.area_fill(colour=0xffcc99),
    CS.area_centertext(colour=0xcc6000,
                       size=30)
]
s['officeArea'] = office_area

residential_office_area = CTI("area")
residential_office_area[0:5] = [
    CS.area_fill(colour=0xd9dbb2),
    CS.area_centertext(colour=0x669240,
                       size=30)
]
s['residentialOficeArea'] = residential_office_area

"schoolArea",
"healthArea",
"agricultureArea",
"militaryArea",
"waterLarge",
"waterSmall",
"landLarge",
"landSmall",
"waterway",
"ferryLine",
"grass",
"shrub",
"forest",
"stone",
"sand",
"gate",
"apron",
"taxiway",
"runway",
"helipad",
"plaza",
"building_underground",
"transportBuilding_underground",
"platform_underground",
"park",
"pathway_underground",
"localHighwaySlip_underground",
"bRoadSlip_underground",
"aRoadSlip_underground",
"localPedestrianQuaternaryRoad_underground",
"localQuaternaryRoad_underground",
"localPedestrianTertiaryRoad_underground",
"localTertiaryRoad_underground",
"localSecondaryRoad_underground",
"localMainRoad_underground",
"localHighway_underground",
"bRoad_underground",
"aRoad_underground",
"rail_underground",
"transportBuilding",
"platform",
"pathway",
"localHighwaySlip",
"bRoadSlip",
"aRoadSlip",
"localPedestrianQuaternaryRoad",
"localQuaternaryRoad",
"localPedestrianTertiaryRoad",
"localTertiaryRoad",
"localSecondaryRoad",
"localMainRoad",
"localHighway",
"bRoad",
"aRoad",
"rail",
"pathway_elevated",
"localHighwaySlip_elevated",
"bRoadSlip_elevated",
"aRoadSlip_elevated",
"localPedestrianQuaternaryRoad_elevated",
"localQuaternaryRoad_elevated",
"localPedestrianTertiaryRoad_elevated",
"localTertiaryRoad_elevated",
"localSecondaryRoad_elevated",
"localMainRoad_elevated",
"localHighway_elevated",
"bRoad_elevated",
"aRoad_elevated",
"rail_elevated",
"building",
"cityHall",
"pedestrianCrossing",
"railCrossing",
"parking",
"bikeRack",
"shop",
"restaurant",
"hotel",
"arcade",
"supermarket",
"clinic",
"library",
"placeOfWorship",
"petrol",
"cinema",
"bank",
"gym",
"shelter",
"playground",
"fountain",
"taxiStand",
"pickUpDropOff",
"busStop",
"ferryStop",
"railStation",
"undergroundExit",
"attraction",
"subdistrict",
"district",
"town",
"state",
"country",
"ward",
"simpleArea",
"simpleLine",
"simplePoint"