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
#manually set these in closure:
"shot_location_exterior",
"shot_location_interior",

"shot_location_nature",
"shot_location_structure",
"shot_location_settlement",

# actual file labels
"shot_location_exterior_nature_beach",
"shot_location_exterior_nature_canyon",
"shot_location_exterior_nature_cave",
"shot_location_exterior_nature_desert",
"shot_location_exterior_nature_forest",
"shot_location_exterior_nature_glacier",
"shot_location_exterior_nature_lake",
"shot_location_exterior_nature_mountains",
"shot_location_exterior_nature_ocean",
"shot_location_exterior_nature_plains",
"shot_location_exterior_nature_polar",
"shot_location_exterior_nature_river",
"shot_location_exterior_nature_sky",
"shot_location_exterior_nature_space",
"shot_location_exterior_nature_wetlands",
"shot_location_exterior_settlement_city",
"shot_location_exterior_settlement_suburb",
"shot_location_exterior_settlement_town",
"shot_location_exterior_structure_bridge",
"shot_location_exterior_structure_building_airport",
"shot_location_exterior_structure_building_auto_body",
"shot_location_exterior_structure_building_castle",
"shot_location_exterior_structure_building_hospital",
"shot_location_exterior_structure_building_houseofworship",
"shot_location_exterior_structure_building_library",
"shot_location_exterior_structure_building_mall",
"shot_location_exterior_structure_building_office",
"shot_location_exterior_structure_building_residence_apartment",
"shot_location_exterior_structure_building_residence_house",
"shot_location_exterior_structure_building_residence_mansion",
"shot_location_exterior_structure_building_residence_monastery",
"shot_location_exterior_structure_building_residence_palace",
"shot_location_exterior_structure_building_restaurant",
"shot_location_exterior_structure_building_school",
"shot_location_exterior_structure_building_skyscraper",
"shot_location_exterior_structure_building_stadium",
"shot_location_exterior_structure_building_station_gas",
"shot_location_exterior_structure_building_station_subway",
"shot_location_exterior_structure_building_station_train",
"shot_location_exterior_structure_building_store",
"shot_location_exterior_structure_building_theater",
"shot_location_exterior_structure_building_warehouse",
"shot_location_exterior_structure_bus_stop",
"shot_location_exterior_structure_farm",
"shot_location_exterior_structure_industrial",
"shot_location_exterior_structure_park",
"shot_location_exterior_structure_parkinglot",
"shot_location_exterior_structure_pier",
"shot_location_exterior_structure_playground",
"shot_location_exterior_structure_port",
"shot_location_exterior_structure_road",
"shot_location_exterior_structure_ruins",
"shot_location_exterior_structure_sidewalk",
"shot_location_exterior_structure_tunnel",
"shot_location_exterior_structure_vehicle_airplane",
"shot_location_exterior_structure_vehicle_bicycle",
"shot_location_exterior_structure_vehicle_boat",
"shot_location_exterior_structure_vehicle_bus",
"shot_location_exterior_structure_vehicle_car",
"shot_location_exterior_structure_vehicle_helicopter",
"shot_location_exterior_structure_vehicle_motorcycle",
"shot_location_exterior_structure_vehicle_spacecraft",
"shot_location_exterior_structure_vehicle_train",
"shot_location_exterior_structure_vehicle_truck",
"shot_location_interior_nature_cave",
"shot_location_interior_structure_building_airport",
"shot_location_interior_structure_building_arena",
"shot_location_interior_structure_building_auditorium",
"shot_location_interior_structure_building_auto_repair_shop",
"shot_location_interior_structure_building_bar",
"shot_location_interior_structure_building_barn",
"shot_location_interior_structure_building_cafe",
"shot_location_interior_structure_building_cafeteria",
"shot_location_interior_structure_building_command_center",
"shot_location_interior_structure_building_crypt",
"shot_location_interior_structure_building_dancefloor",
"shot_location_interior_structure_building_dungeon",
"shot_location_interior_structure_building_elevator",
"shot_location_interior_structure_building_factory",
"shot_location_interior_structure_building_foyer",
"shot_location_interior_structure_building_gym",
"shot_location_interior_structure_building_hallway",
"shot_location_interior_structure_building_hospital",
"shot_location_interior_structure_building_houseofworship",
"shot_location_interior_structure_building_lobby",
"shot_location_interior_structure_building_mall",
"shot_location_interior_structure_building_office",
"shot_location_interior_structure_building_office_cubicle",
"shot_location_interior_structure_building_open_office",
"shot_location_interior_structure_building_prison",
"shot_location_interior_structure_building_restaurant",
"shot_location_interior_structure_building_room_bath",
"shot_location_interior_structure_building_room_bed",
"shot_location_interior_structure_building_room_class",
"shot_location_interior_structure_building_room_closet",
"shot_location_interior_structure_building_room_conference",
"shot_location_interior_structure_building_room_court",
"shot_location_interior_structure_building_room_dining",
"shot_location_interior_structure_building_room_kitchen",
"shot_location_interior_structure_building_room_kitchen_commercial",
"shot_location_interior_structure_building_room_living",
"shot_location_interior_structure_building_room_study",
"shot_location_interior_structure_building_room_throne",
"shot_location_interior_structure_building_stage",
"shot_location_interior_structure_building_stairwell",
"shot_location_interior_structure_building_station_bus",
"shot_location_interior_structure_building_station_fire",
"shot_location_interior_structure_building_station_police",
"shot_location_interior_structure_building_station_subway",
"shot_location_interior_structure_building_station_train",
"shot_location_interior_structure_building_store",
"shot_location_interior_structure_building_store_aisle",
"shot_location_interior_structure_building_store_checkout",
"shot_location_interior_structure_building_warehouse",
"shot_location_interior_structure_vehicle_airplane_cabin",
"shot_location_interior_structure_vehicle_airplane_cockpit",
"shot_location_interior_structure_vehicle_boat",
"shot_location_interior_structure_vehicle_bus",
"shot_location_interior_structure_vehicle_car",
"shot_location_interior_structure_vehicle_helicopter",
"shot_location_interior_structure_vehicle_spacecraft",
"shot_location_interior_structure_vehicle_subway",
"shot_location_interior_structure_vehicle_train",
"shot_location_interior_structure_vehicle_truck",
]

exclusive_interior = [
]

exclusive_concepts = {
}

# for label in labels:

# 	exclusive_concepts[label] = []


# 	if 'nature' in label:
# 		exclusive_nature_v_structure.append(label)

# 	if 'structure' in label:
# 		exclusive_nature_v_structure.append(label)


# 	if 'interior' in label:
# 		exclusive_interior.append(label)

# 	if 'exterior' in label:
# 		exclusive_nature_v_structure.append(label)


# for label in labels:

# 	if 'nature' in label:

# 	exclusive_concepts[label] = []





# #exterior nature shots cant include any of the following:
# # exclusive_exterior_nature.extend(exclusive_exterior_buildings)
# # exclusive_exterior_nature.extend(exclusive_exterior_township1)
# # exclusive_exterior_nature.extend(exclusive_exterior_township2)
# # exclusive_exterior_nature.extend(exclusive_exterior_vehicles)
# exclusive_exterior_nature.extend(exclusive_interior)
# exclusive_exterior_nature.append("shot_location_interior")

# #exterior building shots cant include any of the following:
# # exclusive_exterior_buildings.extend(exclusive_exterior_nature)
# # exclusive_exterior_buildings.extend(exclusive_exterior_township1)
# # exclusive_exterior_buildings.extend(exclusive_exterior_township2)
# # exclusive_exterior_buildings.extend(exclusive_exterior_vehicles)
# exclusive_exterior_buildings.extend(exclusive_interior)
# exclusive_exterior_buildings.append("shot_location_interior")


# # exclusive_exterior_township1.extend(exclusive_exterior_nature)
# # exclusive_exterior_township1.extend(exclusive_exterior_buildings)
# # exclusive_exterior_township1.extend(exclusive_exterior_township2)
# # exclusive_exterior_township1.extend(exclusive_exterior_vehicles)
# exclusive_exterior_township1.extend(exclusive_interior)
# exclusive_exterior_township1.append("shot_location_interior")


# # exclusive_exterior_township2.extend(exclusive_exterior_nature)
# # exclusive_exterior_township2.extend(exclusive_exterior_buildings)
# # exclusive_exterior_township2.extend(exclusive_exterior_township1)
# # exclusive_exterior_township2.extend(exclusive_exterior_vehicles)
# exclusive_exterior_township2.extend(exclusive_interior)
# exclusive_exterior_township2.append("shot_location_interior")

# # exclusive_exterior_vehicles.extend(exclusive_exterior_nature)
# # exclusive_exterior_vehicles.extend(exclusive_exterior_buildings)
# # exclusive_exterior_vehicles.extend(exclusive_exterior_township1)
# # exclusive_exterior_vehicles.extend(exclusive_exterior_township2)
# exclusive_exterior_vehicles.extend(exclusive_interior)
# exclusive_exterior_vehicles.append("shot_location_interior")

# #interior shots cant include any of the following:
# exclusive_interior.extend(exclusive_exterior_nature)
# exclusive_interior.extend(exclusive_exterior_buildings)
# exclusive_interior.extend(exclusive_exterior_township1)
# exclusive_interior.extend(exclusive_exterior_township2)
# exclusive_interior.extend(exclusive_exterior_vehicles)
# exclusive_interior.append("shot_location_exterior")


# list of exclusive concepts groups:

# exclusive_concepts = {

# "shot_location_interior_" : exclusive_interior,


# # individual concepts
# "shot_location_exterior_beach" : exclusive_exterior_nature,
# "shot_location_exterior_canyon" : exclusive_exterior_nature,
# "shot_location_exterior_cave" : exclusive_exterior_nature,
# "shot_location_exterior_desert" : exclusive_exterior_nature,
# "shot_location_exterior_forest" : exclusive_exterior_nature,
# "shot_location_exterior_glacier" : exclusive_exterior_nature,
# "shot_location_exterior_lake" : exclusive_exterior_nature,
# "shot_location_exterior_mountains" : exclusive_exterior_nature,
# "shot_location_exterior_ocean" : exclusive_exterior_nature,
# "shot_location_exterior_plains" : exclusive_exterior_nature,
# "shot_location_exterior_polar" : exclusive_exterior_nature,
# "shot_location_exterior_river" : exclusive_exterior_nature,
# "shot_location_exterior_sky" : exclusive_exterior_nature,
# "shot_location_exterior_space" : exclusive_exterior_nature,
# "shot_location_exterior_wetlands" : exclusive_exterior_nature,

# "shot_location_exterior_airport" : exclusive_exterior_buildings,
# "shot_location_exterior_apartment" : exclusive_exterior_buildings,
# "shot_location_exterior_auto_body" : exclusive_exterior_buildings,
# "shot_location_exterior_bridge" : exclusive_exterior_buildings,
# "shot_location_exterior_bus_stop" : exclusive_exterior_buildings,
# "shot_location_exterior_castle" : exclusive_exterior_buildings,
# "shot_location_exterior_cathedral" : exclusive_exterior_buildings,
# "shot_location_exterior_church" : exclusive_exterior_buildings,
# "shot_location_exterior_farm" : exclusive_exterior_buildings,
# "shot_location_exterior_hospital" : exclusive_exterior_buildings,
# "shot_location_exterior_house" : exclusive_exterior_buildings,
# "shot_location_exterior_houseofworship" : exclusive_exterior_buildings,
# "shot_location_exterior_industrial" : exclusive_exterior_buildings,
# "shot_location_exterior_library" : exclusive_exterior_buildings,
# "shot_location_exterior_mall" : exclusive_exterior_buildings,
# "shot_location_exterior_mansion" : exclusive_exterior_buildings,
# "shot_location_exterior_monastery" : exclusive_exterior_buildings,
# "shot_location_exterior_mosque" : exclusive_exterior_buildings,
# "shot_location_exterior_office" : exclusive_exterior_buildings,
# "shot_location_exterior_palace" : exclusive_exterior_buildings,
# "shot_location_exterior_parkinglot" : exclusive_exterior_buildings,
# "shot_location_exterior_pier" : exclusive_exterior_buildings,
# "shot_location_exterior_port" : exclusive_exterior_buildings,
# "shot_location_exterior_restaurant" : exclusive_exterior_buildings,
# "shot_location_exterior_ruins" : exclusive_exterior_buildings,
# "shot_location_exterior_school" : exclusive_exterior_buildings,
# "shot_location_exterior_skyscraper" : exclusive_exterior_buildings,
# "shot_location_exterior_stadium" : exclusive_exterior_buildings,
# "shot_location_exterior_station_gas" : exclusive_exterior_buildings,
# "shot_location_exterior_station_subway" : exclusive_exterior_buildings,
# "shot_location_exterior_station_train" : exclusive_exterior_buildings,
# "shot_location_exterior_store" : exclusive_exterior_buildings,
# "shot_location_exterior_synagogue" : exclusive_exterior_buildings,
# "shot_location_exterior_temple" : exclusive_exterior_buildings,
# "shot_location_exterior_theater" : exclusive_exterior_buildings,
# "shot_location_exterior_tunnel" : exclusive_exterior_buildings,
# "shot_location_exterior_warehouse" : exclusive_exterior_buildings,

# "shot_location_exterior_city" : exclusive_exterior_township1,
# "shot_location_exterior_suburb" : exclusive_exterior_township1,
# "shot_location_exterior_town" : exclusive_exterior_township1,

# "shot_location_exterior_park" : exclusive_exterior_township2, 
# "shot_location_exterior_playground" : exclusive_exterior_township2, 
# "shot_location_exterior_road" : exclusive_exterior_township2, 
# "shot_location_exterior_sidewalk" : exclusive_exterior_township2, 

# "shot_location_exterior_airplane": exclusive_exterior_vehicles,
# "shot_location_exterior_bicycle": exclusive_exterior_vehicles,
# "shot_location_exterior_boat": exclusive_exterior_vehicles,
# "shot_location_exterior_bus": exclusive_exterior_vehicles,
# "shot_location_exterior_car": exclusive_exterior_vehicles,
# "shot_location_exterior_helicopter": exclusive_exterior_vehicles,
# "shot_location_exterior_motorcycle": exclusive_exterior_vehicles,
# "shot_location_exterior_spacecraft": exclusive_exterior_vehicles,
# "shot_location_exterior_train": exclusive_exterior_vehicles,
# "shot_location_exterior_truck": exclusive_exterior_vehicles,
# }


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



def custom_label_closure(file_concept, labels, file_label_value):

	# recurse through our image directory and determine the known positive label (1) known negative labels (0), and unknown labels (-1)
	positive = "1"
	negative = "0"
	unknown = "-1"


	print("custom_label_closure")
	# mark any specific interior or exterior concept as true for the  interior or exterior master label
	# and ensure all opposites are 0 - (and exterior anything cant be an interior anything, and vice versa) 
	if 'exterior' in file_concept:
		index = labels.index('shot_location_exterior')
		file_label_value[index] = positive

		#if we have an exterior mark all interiors and negative
		for label in labels:
			if 'interior' in label:
				index = labels.index(label)
				file_label_value[index] = negative

	if 'interior' in file_concept:
		index = labels.index('shot_location_interior')
		file_label_value[index] = positive

		#if we have an interior mark all exteriors and negative
		for label in labels:
			if 'exterior' in label:
				index = labels.index(label)
				file_label_value[index] = negative

	if 'nature' in file_concept:
		index = labels.index('shot_location_nature')
		file_label_value[index] = positive

	if 'structure' in file_concept:
		index = labels.index('shot_location_structure')
		file_label_value[index] = positive
				
	if 'settlement' in file_concept:
		index = labels.index('shot_location_settlement')
		file_label_value[index] = positive

	return file_label_value
										


auto_label.auto_label(args, labels, labels, not_applicable_key, not_applicable_concepts, custom_label_closure)


