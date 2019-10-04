import os 
import csv   
import argparse
import random
import math
import time
import json
import auto_label

parser = argparse.ArgumentParser(description='Use a folder of ML model classifiers to label a local unlabeled data set')
parser.add_argument('-i', '--imagedir', type=str, help="folder containing unlabeled images to be labeled", default="./images", required=True)
parser.add_argument('-o', '--output', type=str, help="destination for labeled file containing multi labels", default="./labels", required=False)
parser.add_argument('-pre', '--prefix', type=str, help="image url prefix, useful for adding a cloud storage provider URLs to the CSV path", default="", required=False)
parser.add_argument('-l', '--limit', type=int, help="limit the number of images we label - useful for testing", default="1000000000000", required=False)
parser.add_argument('-r', '--random', type=bool, help="limit the number of images we label - useful for testing", default=False, required=False)

args = parser.parse_args()


################
# NOTE THAT APPLICABLE LABELS / CONCEPTS MUST EXACTLY MATCH ON DISK FOLDER NAMES
################

labels = [
"shot_location_exterior",
"shot_location_exterior_airplane",
"shot_location_exterior_airport",
"shot_location_exterior_apartment",
"shot_location_exterior_auto_body",
"shot_location_exterior_beach",
"shot_location_exterior_bicycle",
"shot_location_exterior_boat",
"shot_location_exterior_bridge",
"shot_location_exterior_bus",
"shot_location_exterior_bus_stop",
"shot_location_exterior_canyon",
"shot_location_exterior_car",
"shot_location_exterior_castle",
"shot_location_exterior_cathedral",
"shot_location_exterior_cave",
"shot_location_exterior_church",
"shot_location_exterior_city",
"shot_location_exterior_desert",
"shot_location_exterior_farm",
"shot_location_exterior_forest",
"shot_location_exterior_glacier",
"shot_location_exterior_helicopter",
"shot_location_exterior_hospital",
"shot_location_exterior_house",
"shot_location_exterior_industrial",
"shot_location_exterior_lake",
"shot_location_exterior_library",
"shot_location_exterior_mall",
"shot_location_exterior_mansion",
"shot_location_exterior_monastery",
"shot_location_exterior_mosque",
"shot_location_exterior_motorcycle",
"shot_location_exterior_mountains",
"shot_location_exterior_ocean",
"shot_location_exterior_office",
"shot_location_exterior_palace",
"shot_location_exterior_park",
"shot_location_exterior_parkinglot",
"shot_location_exterior_pier",
"shot_location_exterior_plains",
"shot_location_exterior_playground",
"shot_location_exterior_polar",
"shot_location_exterior_port",
"shot_location_exterior_restaurant",
"shot_location_exterior_river",
"shot_location_exterior_road",
"shot_location_exterior_ruins",
"shot_location_exterior_school",
"shot_location_exterior_sidewalk",
"shot_location_exterior_sky",
"shot_location_exterior_skyscraper",
"shot_location_exterior_space",
"shot_location_exterior_spacecraft",
"shot_location_exterior_stadium",
"shot_location_exterior_station_gas",
"shot_location_exterior_station_subway",
"shot_location_exterior_station_train",
"shot_location_exterior_store",
"shot_location_exterior_suburb",
"shot_location_exterior_synagogue",
"shot_location_exterior_temple",
"shot_location_exterior_theater",
"shot_location_exterior_town",
"shot_location_exterior_train",
"shot_location_exterior_truck",
"shot_location_exterior_tunnel",
"shot_location_exterior_warehouse",
"shot_location_exterior_wetlands",
"shot_location_interior",
"shot_location_interior_airplane_cabin",
"shot_location_interior_airplane_cockpit",
"shot_location_interior_airport",
"shot_location_interior_arena",
"shot_location_interior_auditorium",
"shot_location_interior_auto_repair_shop",
"shot_location_interior_bar",
"shot_location_interior_barn",
"shot_location_interior_bathroom",
"shot_location_interior_bedroom",
"shot_location_interior_boat",
"shot_location_interior_bus",
"shot_location_interior_cafe",
"shot_location_interior_cafeteria",
"shot_location_interior_car",
"shot_location_interior_cave",
"shot_location_interior_classroom",
"shot_location_interior_cloister",
"shot_location_interior_closet",
"shot_location_interior_command_center",
"shot_location_interior_commercialkitchen",
"shot_location_interior_conferenceroom",
"shot_location_interior_courtroom",
"shot_location_interior_crypt",
"shot_location_interior_dancefloor",
"shot_location_interior_diningroom",
"shot_location_interior_dungeon",
"shot_location_interior_elevator",
"shot_location_interior_factory",
"shot_location_interior_foyer",
"shot_location_interior_gym",
"shot_location_interior_hallway",
"shot_location_interior_helicopter",
"shot_location_interior_hospital",
"shot_location_interior_kitchen",
"shot_location_interior_livingroom",
"shot_location_interior_lobby",
"shot_location_interior_mall",
"shot_location_interior_meditation",
"shot_location_interior_nave",
"shot_location_interior_office",
"shot_location_interior_office_cubicle",
"shot_location_interior_office_open",
"shot_location_interior_prayer_hall",
"shot_location_interior_prison",
"shot_location_interior_pulpit",
"shot_location_interior_restaurant",
"shot_location_interior_spacecraft",
"shot_location_interior_stage",
"shot_location_interior_stairwell",
"shot_location_interior_station_bus",
"shot_location_interior_station_fire",
"shot_location_interior_station_police",
"shot_location_interior_station_subway",
"shot_location_interior_station_train",
"shot_location_interior_store",
"shot_location_interior_store_aisle",
"shot_location_interior_store_checkout",
"shot_location_interior_study",
"shot_location_interior_subway",
"shot_location_interior_synagogue",
"shot_location_interior_throneroom",
"shot_location_interior_train",
"shot_location_interior_truck",
"shot_location_interior_warehouse",
]

exclusive_exterior_nature = [
"shot_location_exterior_beach",
"shot_location_exterior_canyon",
"shot_location_exterior_cave",
"shot_location_exterior_desert",
"shot_location_exterior_forest",
"shot_location_exterior_glacier",
"shot_location_exterior_lake",
"shot_location_exterior_mountains",
"shot_location_exterior_ocean",
"shot_location_exterior_plains",
"shot_location_exterior_polar",
"shot_location_exterior_river",
"shot_location_exterior_sky",
"shot_location_exterior_space",
"shot_location_exterior_wetlands",
]

exclusive_exterior_buildings = [
"shot_location_exterior_airport",
"shot_location_exterior_apartment",
"shot_location_exterior_auto_body",
"shot_location_exterior_bridge",
"shot_location_exterior_bus_stop",
"shot_location_exterior_castle",
"shot_location_exterior_cathedral",
"shot_location_exterior_church",
"shot_location_exterior_farm",
"shot_location_exterior_hospital",
"shot_location_exterior_house",
"shot_location_exterior_industrial",
"shot_location_exterior_library",
"shot_location_exterior_mall",
"shot_location_exterior_mansion",
"shot_location_exterior_monastery",
"shot_location_exterior_mosque",
"shot_location_exterior_office",
"shot_location_exterior_palace",
"shot_location_exterior_parkinglot",
"shot_location_exterior_pier",
"shot_location_exterior_port",
"shot_location_exterior_restaurant",
"shot_location_exterior_ruins",
"shot_location_exterior_school",
"shot_location_exterior_skyscraper",
"shot_location_exterior_stadium",
"shot_location_exterior_station_gas",
"shot_location_exterior_station_subway",
"shot_location_exterior_station_train",
"shot_location_exterior_store",
"shot_location_exterior_synagogue",
"shot_location_exterior_temple",
"shot_location_exterior_theater",
"shot_location_exterior_tunnel",
"shot_location_exterior_warehouse"
]

exclusive_exterior_township1 = [
"shot_location_exterior_city",
"shot_location_exterior_suburb",
"shot_location_exterior_town",
]

exclusive_exterior_township2 = [
"shot_location_exterior_park",
"shot_location_exterior_playground",
"shot_location_exterior_road",
"shot_location_exterior_sidewalk",
]

exclusive_exterior_vehicles = [
"shot_location_exterior_airplane",
"shot_location_exterior_bicycle",
"shot_location_exterior_boat",
"shot_location_exterior_bus",
"shot_location_exterior_car",
"shot_location_exterior_helicopter",
"shot_location_exterior_motorcycle",
"shot_location_exterior_spacecraft",
"shot_location_exterior_train",
"shot_location_exterior_truck",
]


exclusive_interior = [
"shot_location_interior_airplane_cabin",
"shot_location_interior_airplane_cockpit",
"shot_location_interior_airport",
"shot_location_interior_arena",
"shot_location_interior_auditorium",
"shot_location_interior_auto_repair_shop",
"shot_location_interior_bar",
"shot_location_interior_barn",
"shot_location_interior_bathroom",
"shot_location_interior_bedroom",
"shot_location_interior_boat",
"shot_location_interior_bus",
"shot_location_interior_cafe",
"shot_location_interior_cafeteria",
"shot_location_interior_car",
"shot_location_interior_cave",
"shot_location_interior_classroom",
"shot_location_interior_cloister",
"shot_location_interior_closet",
"shot_location_interior_command_center",
"shot_location_interior_commercialkitchen",
"shot_location_interior_conferenceroom",
"shot_location_interior_courtroom",
"shot_location_interior_crypt",
"shot_location_interior_dancefloor",
"shot_location_interior_diningroom",
"shot_location_interior_dungeon",
"shot_location_interior_elevator",
"shot_location_interior_factory",
"shot_location_interior_foyer",
"shot_location_interior_gym",
"shot_location_interior_hallway",
"shot_location_interior_helicopter",
"shot_location_interior_hospital",
"shot_location_interior_kitchen",
"shot_location_interior_livingroom",
"shot_location_interior_lobby",
"shot_location_interior_mall",
"shot_location_interior_meditation",
"shot_location_interior_nave",
"shot_location_interior_office",
"shot_location_interior_office_cubicle",
"shot_location_interior_office_open",
"shot_location_interior_prayer_hall",
"shot_location_interior_prison",
"shot_location_interior_pulpit",
"shot_location_interior_restaurant",
"shot_location_interior_spacecraft",
"shot_location_interior_stage",
"shot_location_interior_stairwell",
"shot_location_interior_station_bus",
"shot_location_interior_station_fire",
"shot_location_interior_station_police",
"shot_location_interior_station_subway",
"shot_location_interior_station_train",
"shot_location_interior_store",
"shot_location_interior_store_aisle",
"shot_location_interior_store_checkout",
"shot_location_interior_study",
"shot_location_interior_subway",
"shot_location_interior_synagogue",
"shot_location_interior_throneroom",
"shot_location_interior_train",
"shot_location_interior_truck",
"shot_location_interior_warehouse"
]

#exterior nature shots cant include any of the following:
exclusive_exterior_nature.extend(exclusive_exterior_buildings)
exclusive_exterior_nature.extend(exclusive_exterior_township1)
exclusive_exterior_nature.extend(exclusive_exterior_township2)
exclusive_exterior_nature.extend(exclusive_exterior_vehicles)
exclusive_exterior_nature.extend(exclusive_interior)
exclusive_exterior_nature.append("shot_location_interior")

#exterior building shots cant include any of the following:
exclusive_exterior_buildings.extend(exclusive_exterior_nature)
exclusive_exterior_buildings.extend(exclusive_exterior_township1)
exclusive_exterior_buildings.extend(exclusive_exterior_township2)
exclusive_exterior_buildings.extend(exclusive_exterior_vehicles)
exclusive_exterior_buildings.extend(exclusive_interior)
exclusive_exterior_buildings.append("shot_location_interior")


exclusive_exterior_township1.extend(exclusive_exterior_nature)
exclusive_exterior_township1.extend(exclusive_exterior_buildings)
exclusive_exterior_township1.extend(exclusive_exterior_township2)
exclusive_exterior_township1.extend(exclusive_exterior_vehicles)
exclusive_exterior_township1.extend(exclusive_interior)
exclusive_exterior_township1.append("shot_location_interior")


exclusive_exterior_township2.extend(exclusive_exterior_nature)
exclusive_exterior_township2.extend(exclusive_exterior_buildings)
exclusive_exterior_township2.extend(exclusive_exterior_township1)
exclusive_exterior_township2.extend(exclusive_exterior_vehicles)
exclusive_exterior_township2.extend(exclusive_interior)
exclusive_exterior_township2.append("shot_location_interior")

exclusive_exterior_vehicles.extend(exclusive_exterior_nature)
exclusive_exterior_vehicles.extend(exclusive_exterior_buildings)
exclusive_exterior_vehicles.extend(exclusive_exterior_township1)
exclusive_exterior_vehicles.extend(exclusive_exterior_township2)
exclusive_exterior_vehicles.extend(exclusive_interior)
exclusive_exterior_vehicles.append("shot_location_interior")

#interior shots cant include any of the following:
exclusive_interior.extend(exclusive_exterior_nature)
exclusive_interior.extend(exclusive_exterior_buildings)
exclusive_interior.extend(exclusive_exterior_township1)
exclusive_interior.extend(exclusive_exterior_township2)
exclusive_interior.extend(exclusive_exterior_vehicles)
exclusive_interior.append("shot_location_exterior")


# list of exclusive concepts groups:

exclusive_concepts = {

"shot_location_interior_" : exclusive_interior,


# individual concepts
"shot_location_exterior_beach" : exclusive_exterior_nature,
"shot_location_exterior_canyon" : exclusive_exterior_nature,
"shot_location_exterior_cave" : exclusive_exterior_nature,
"shot_location_exterior_desert" : exclusive_exterior_nature,
"shot_location_exterior_forest" : exclusive_exterior_nature,
"shot_location_exterior_glacier" : exclusive_exterior_nature,
"shot_location_exterior_lake" : exclusive_exterior_nature,
"shot_location_exterior_mountains" : exclusive_exterior_nature,
"shot_location_exterior_ocean" : exclusive_exterior_nature,
"shot_location_exterior_plains" : exclusive_exterior_nature,
"shot_location_exterior_polar" : exclusive_exterior_nature,
"shot_location_exterior_river" : exclusive_exterior_nature,
"shot_location_exterior_sky" : exclusive_exterior_nature,
"shot_location_exterior_space" : exclusive_exterior_nature,
"shot_location_exterior_wetlands" : exclusive_exterior_nature,

"shot_location_exterior_airport" : exclusive_exterior_buildings,
"shot_location_exterior_apartment" : exclusive_exterior_buildings,
"shot_location_exterior_auto_body" : exclusive_exterior_buildings,
"shot_location_exterior_bridge" : exclusive_exterior_buildings,
"shot_location_exterior_bus_stop" : exclusive_exterior_buildings,
"shot_location_exterior_castle" : exclusive_exterior_buildings,
"shot_location_exterior_cathedral" : exclusive_exterior_buildings,
"shot_location_exterior_church" : exclusive_exterior_buildings,
"shot_location_exterior_farm" : exclusive_exterior_buildings,
"shot_location_exterior_hospital" : exclusive_exterior_buildings,
"shot_location_exterior_house" : exclusive_exterior_buildings,
"shot_location_exterior_industrial" : exclusive_exterior_buildings,
"shot_location_exterior_library" : exclusive_exterior_buildings,
"shot_location_exterior_mall" : exclusive_exterior_buildings,
"shot_location_exterior_mansion" : exclusive_exterior_buildings,
"shot_location_exterior_monastery" : exclusive_exterior_buildings,
"shot_location_exterior_mosque" : exclusive_exterior_buildings,
"shot_location_exterior_office" : exclusive_exterior_buildings,
"shot_location_exterior_palace" : exclusive_exterior_buildings,
"shot_location_exterior_parkinglot" : exclusive_exterior_buildings,
"shot_location_exterior_pier" : exclusive_exterior_buildings,
"shot_location_exterior_port" : exclusive_exterior_buildings,
"shot_location_exterior_restaurant" : exclusive_exterior_buildings,
"shot_location_exterior_ruins" : exclusive_exterior_buildings,
"shot_location_exterior_school" : exclusive_exterior_buildings,
"shot_location_exterior_skyscraper" : exclusive_exterior_buildings,
"shot_location_exterior_stadium" : exclusive_exterior_buildings,
"shot_location_exterior_station_gas" : exclusive_exterior_buildings,
"shot_location_exterior_station_subway" : exclusive_exterior_buildings,
"shot_location_exterior_station_train" : exclusive_exterior_buildings,
"shot_location_exterior_store" : exclusive_exterior_buildings,
"shot_location_exterior_synagogue" : exclusive_exterior_buildings,
"shot_location_exterior_temple" : exclusive_exterior_buildings,
"shot_location_exterior_theater" : exclusive_exterior_buildings,
"shot_location_exterior_tunnel" : exclusive_exterior_buildings,
"shot_location_exterior_warehouse" : exclusive_exterior_buildings,

"shot_location_exterior_city" : exclusive_exterior_township1,
"shot_location_exterior_suburb" : exclusive_exterior_township1,
"shot_location_exterior_town" : exclusive_exterior_township1,

"shot_location_exterior_park" : exclusive_exterior_township2, 
"shot_location_exterior_playground" : exclusive_exterior_township2, 
"shot_location_exterior_road" : exclusive_exterior_township2, 
"shot_location_exterior_sidewalk" : exclusive_exterior_township2, 

"shot_location_exterior_airplane": exclusive_exterior_vehicles,
"shot_location_exterior_bicycle": exclusive_exterior_vehicles,
"shot_location_exterior_boat": exclusive_exterior_vehicles,
"shot_location_exterior_bus": exclusive_exterior_vehicles,
"shot_location_exterior_car": exclusive_exterior_vehicles,
"shot_location_exterior_helicopter": exclusive_exterior_vehicles,
"shot_location_exterior_motorcycle": exclusive_exterior_vehicles,
"shot_location_exterior_spacecraft": exclusive_exterior_vehicles,
"shot_location_exterior_train": exclusive_exterior_vehicles,
"shot_location_exterior_truck": exclusive_exterior_vehicles,
}


################
# NOTE THAT NOT APPLICABLE LABELS / CONCEPTS MUST EXACTLY MATCH ON DISK FOLDER NAMES
# NOT APPLICABLE CONCEPTS ARE MARKED AS FALSE FOR ALL LABELS EXCEPT THEIR OWN
################


# unsure if a key is applicable.
# we could just mark 0 in all of the above keys and be done with it?
# but not applicable is a good signal tho too?
not_applicable_key = "shot_location_na"

not_applicable_concepts = [

# cant discern location from this:
"shot_framing_extremecloseup",
"texture"
]

auto_label.auto_label(args, labels, exclusive_concepts, not_applicable_key, not_applicable_concepts)


