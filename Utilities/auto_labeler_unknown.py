import os 
import csv   
import argparse
import random
import math
import time
import json

parser = argparse.ArgumentParser(description='Use a folder of ML model classifiers to label a local unlabeled data set')
parser.add_argument('-i', '--imagedir', type=str, help="folder containing unlabeled images to be labeled", default="./images", required=True)
parser.add_argument('-o', '--output', type=str, help="destination for labeled file containing multi labels", default="./labels", required=False)
parser.add_argument('-pre', '--prefix', type=str, help="image url prefix, useful for adding a cloud storage provider URLs to the CSV path", default="", required=False)
parser.add_argument('-l', '--limit', type=int, help="limit the number of images we label - useful for testing", default="1000000000000", required=False)
parser.add_argument('-r', '--random', type=bool, help="limit the number of images we label - useful for testing", default=False, required=False)

args = parser.parse_args()

# load our models into our models array
dir_path = os.getcwd()


# recurse through our image directory and determine the known positive label (1) known negative labels (0), and unknown labels (-1)
positive = "1"
negative = "0"
unknown = "-1"

labels = [
"color_key_blue",
"color_key_green",
"color_key_luma",
"color_key_matte",
"color_saturation_desaturated",
"color_saturation_neutral",
"color_saturation_pastel",
"color_saturation_saturated",
"color_theory_analagous",
"color_theory_complementary",
"color_theory_monochrome",
"color_tones_blackwhite",
"color_tones_cool",
"color_tones_warm",
"exterior",
"exterior_airplane",
"exterior_airport",
"exterior_apartment",
"exterior_auto_body",
"exterior_beach",
"exterior_bicycle",
"exterior_boat",
"exterior_bridge",
"exterior_bus",
"exterior_bus_stop",
"exterior_canyon",
"exterior_car",
"exterior_castle",
"exterior_cathedral",
"exterior_cave",
"exterior_church",
"exterior_city",
"exterior_desert",
"exterior_farm",
"exterior_forest",
"exterior_glacier",
"exterior_helicopter",
"exterior_hospital",
"exterior_house",
"exterior_industrial",
"exterior_lake",
"exterior_library",
"exterior_mall",
"exterior_mansion",
"exterior_monastery",
"exterior_mosque",
"exterior_motorcycle",
"exterior_mountains",
"exterior_ocean",
"exterior_office",
"exterior_palace",
"exterior_park",
"exterior_parkinglot",
"exterior_pier",
"exterior_plains",
"exterior_playground",
"exterior_polar",
"exterior_port",
"exterior_restaurant",
"exterior_river",
"exterior_road",
"exterior_ruins",
"exterior_school",
"exterior_sidewalk",
"exterior_sky",
"exterior_skyscraper",
"exterior_space",
"exterior_spacecraft",
"exterior_stadium",
"exterior_station_gas",
"exterior_station_subway",
"exterior_station_train",
"exterior_store",
"exterior_suburb",
"exterior_synagogue",
"exterior_temple",
"exterior_theater",
"exterior_town",
"exterior_train",
"exterior_truck",
"exterior_tunnel",
"exterior_warehouse",
"exterior_wetlands",
"interior",
"interior_airplane_cabin",
"interior_airplane_cockpit",
"interior_airport",
"interior_arena",
"interior_auditorium",
"interior_auto_repair_shop",
"interior_bar",
"interior_barn",
"interior_bathroom",
"interior_bedroom",
"interior_boat",
"interior_bus",
"interior_cafe",
"interior_cafeteria",
"interior_car",
"interior_cave",
"interior_classroom",
"interior_cloister",
"interior_closet",
"interior_command_center",
"interior_commercialkitchen",
"interior_conferenceroom",
"interior_courtroom",
"interior_crypt",
"interior_dancefloor",
"interior_diningroom",
"interior_dungeon",
"interior_elevator",
"interior_factory",
"interior_foyer",
"interior_gym",
"interior_hallway",
"interior_helicopter",
"interior_hospital",
"interior_kitchen",
"interior_livingroom",
"interior_lobby",
"interior_mall",
"interior_meditation",
"interior_nave",
"interior_office",
"interior_office_cubicle",
"interior_office_open",
"interior_prayer_hall",
"interior_prison",
"interior_pulpit",
"interior_restaurant",
"interior_spacecraft",
"interior_stage",
"interior_stairwell",
"interior_station_bus",
"interior_station_fire",
"interior_station_police",
"interior_station_subway",
"interior_station_train",
"interior_store",
"interior_store_aisle",
"interior_store_checkout",
"interior_study",
"interior_subway",
"interior_synagogue",
"interior_throneroom",
"interior_train",
"interior_truck",
"interior_warehouse",
"shot_angle_aerial",
"shot_angle_eyelevel",
"shot_angle_high",
"shot_angle_low",
"shot_focus_deep",
"shot_focus_out",
"shot_focus_shallow",
"shot_framing_closeup",
"shot_framing_extemelong",
"shot_framing_extremecloseup",
"shot_framing_long",
"shot_framing_medium",
"shot_level_level",
"shot_level_tilted",
"shot_lighting_hard",
"shot_lighting_key_high",
"shot_lighting_key_low",
"shot_lighting_silhouette",
"shot_lighting_soft",
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",
"shot_subject_text",
"shot_timeofday_day",
"shot_timeofday_night",
"shot_timeofday_twilight",
"shot_type_master",
"shot_type_overtheshoulder",
"shot_type_portrait",
"shot_type_twoshot",
"texture_banded",
"texture_blotchy",
"texture_braided",
"texture_bubbly",
"texture_bumpy",
"texture_chequered",
"texture_cobwebbed",
"texture_cracked",
"texture_crosshatched",
"texture_crystalline",
"texture_dotted",
"texture_fibrous",
"texture_flecked",
"texture_frilly",
"texture_gauzy",
"texture_grid",
"texture_grooved",
"texture_honeycombed",
"texture_interlaced",
"texture_knitted",
"texture_lacelike",
"texture_lined",
"texture_marbled",
"texture_matted",
"texture_meshed",
"texture_paisley",
"texture_perforated",
"texture_pitted",
"texture_pleated",
"texture_porous",
"texture_potholed",
"texture_scaly",
"texture_smeared",
"texture_spiralled",
"texture_sprinkled",
"texture_stained",
"texture_stratified",
"texture_striped",
"texture_studded",
"texture_swirly",
"texture_veined",
"texture_waffled",
"texture_woven",
"texture_wrinkled",
"texture_zigzagged"
]

# list of exclusive concepts groups:
exclusive_color_key = [
"color_key_blue",
"color_key_green",
"color_key_luma",
"color_key_matte",
"interior",
"exterior"
]

exclusive_color_saturation = [
"color_saturation_desaturated",
"color_saturation_neutral",
"color_saturation_pastel",
"color_saturation_saturated"
]

exclusive_color_theory = [
"color_theory_analagous",
"color_theory_complementary",
"color_theory_monochrome"
]

exclusive_color_tones = [
"color_tones_blackwhite",
"color_tones_cool",
"color_tones_warm"
]

exclusive_exterior_nature = [
"exterior_beach",
"exterior_canyon",
"exterior_cave",
"exterior_desert",
"exterior_forest",
"exterior_glacier",
"exterior_lake",
"exterior_mountains",
"exterior_ocean",
"exterior_plains",
"exterior_polar",
"exterior_river",
"exterior_sky",
"exterior_space",
"exterior_wetlands",
]

exclusive_exterior_buildings = [
"exterior_airport",
"exterior_apartment",
"exterior_auto_body",
"exterior_bridge",
"exterior_bus_stop",
"exterior_castle",
"exterior_cathedral",
"exterior_church",
"exterior_farm",
"exterior_hospital",
"exterior_house",
"exterior_industrial",
"exterior_library",
"exterior_mall",
"exterior_mansion",
"exterior_monastery",
"exterior_mosque",
"exterior_office",
"exterior_palace",
"exterior_parkinglot",
"exterior_pier",
"exterior_port",
"exterior_restaurant",
"exterior_ruins",
"exterior_school",
"exterior_skyscraper",
"exterior_stadium",
"exterior_station_gas",
"exterior_station_subway",
"exterior_station_train",
"exterior_store",
"exterior_synagogue",
"exterior_temple",
"exterior_theater",
"exterior_tunnel",
"exterior_warehouse"
]

exclusive_exterior_township1 = [
"exterior_city",
"exterior_suburb",
"exterior_town",
]

exclusive_exterior_township2 = [
"exterior_park",
"exterior_playground",
"exterior_road",
"exterior_sidewalk",
]

exclusive_exterior_vehicles = [
"exterior_airplane",
"exterior_bicycle",
"exterior_boat",
"exterior_bus",
"exterior_car",
"exterior_helicopter",
"exterior_motorcycle",
"exterior_spacecraft",
"exterior_train",
"exterior_truck",
]


exclusive_interior = [
"interior_airplane_cabin",
"interior_airplane_cockpit",
"interior_airport",
"interior_arena",
"interior_auditorium",
"interior_auto_repair_shop",
"interior_bar",
"interior_barn",
"interior_bathroom",
"interior_bedroom",
"interior_boat",
"interior_bus",
"interior_cafe",
"interior_cafeteria",
"interior_car",
"interior_cave",
"interior_classroom",
"interior_cloister",
"interior_closet",
"interior_command_center",
"interior_commercialkitchen",
"interior_conferenceroom",
"interior_courtroom",
"interior_crypt",
"interior_dancefloor",
"interior_diningroom",
"interior_dungeon",
"interior_elevator",
"interior_factory",
"interior_foyer",
"interior_gym",
"interior_hallway",
"interior_helicopter",
"interior_hospital",
"interior_kitchen",
"interior_livingroom",
"interior_lobby",
"interior_mall",
"interior_meditation",
"interior_nave",
"interior_office",
"interior_office_cubicle",
"interior_office_open",
"interior_prayer_hall",
"interior_prison",
"interior_pulpit",
"interior_restaurant",
"interior_spacecraft",
"interior_stage",
"interior_stairwell",
"interior_station_bus",
"interior_station_fire",
"interior_station_police",
"interior_station_subway",
"interior_station_train",
"interior_store",
"interior_store_aisle",
"interior_store_checkout",
"interior_study",
"interior_subway",
"interior_synagogue",
"interior_throneroom",
"interior_train",
"interior_truck",
"interior_warehouse"
]

exclusive_shot_angle = [
"shot_angle_aerial",
"shot_angle_eyelevel",
"shot_angle_high",
"shot_angle_low",
]

exclusive_shot_focus = [
"shot_focus_deep",
"shot_focus_out",
"shot_focus_shallow",
]

exclusive_shot_framing = [
"shot_framing_closeup",
"shot_framing_extemelong",
"shot_framing_extremecloseup",
"shot_framing_long",
"shot_framing_medium",
]

exclusive_shot_level = [
"shot_level_level",
"shot_level_tilted"
]

exclusive_shot_lighting_hard = [
"shot_lighting_hard",
"shot_lighting_soft"
]

exclusive_shot_lighting_key = [
"shot_lighting_key_high",
"shot_lighting_key_low"
]

exclusive_shot_timeofday = [
"shot_timeofday_day",
"shot_timeofday_night",
"shot_timeofday_twilight"
]

exclusive_shot_type = [
"shot_type_master",
"shot_type_portrait",
"shot_type_twoshot"
# OTS is not exclusive - could be a OTS Master, Two Shot or Portrait
#"shot_type_overtheshoulder",
]

exclusive_shot_subject = [
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",
"shot_subject_text"

]

exclusive_shot_subject_body = [
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",
]

#strictly speaking texture is not exclusive but for brevity we treat it as such now
exclusive_texture = [
"texture_banded",
"texture_blotchy",
"texture_braided",
"texture_bubbly",
"texture_bumpy",
"texture_chequered",
"texture_cobwebbed",
"texture_cracked",
"texture_crosshatched",
"texture_crystalline",
"texture_dotted",
"texture_fibrous",
"texture_flecked",
"texture_frilly",
"texture_gauzy",
"texture_grid",
"texture_grooved",
"texture_honeycombed",
"texture_interlaced",
"texture_knitted",
"texture_lacelike",
"texture_lined",
"texture_marbled",
"texture_matted",
"texture_meshed",
"texture_paisley",
"texture_perforated",
"texture_pitted",
"texture_pleated",
"texture_porous",
"texture_potholed",
"texture_scaly",
"texture_smeared",
"texture_spiralled",
"texture_sprinkled",
"texture_stained",
"texture_stratified",
"texture_striped",
"texture_studded",
"texture_swirly",
"texture_veined",
"texture_waffled",
"texture_woven",
"texture_wrinkled",
"texture_zigzagged"
]



# all valid files we will label
all_files = []

# for every file, an array of [1, 0, -1] to represent the label for that index's known state.
all_files_label_values = []

with open(args.output, 'wb') as writer:

	writer = csv.writer(writer)

	################
	# extend our list of exclusive concepts:
	# note - this isnt all strictly TRUE, but its helpful to limit the free dimensions of the model
	# considering our data set isnt exhaustively labeled.
	################


	# almost positive none of these contain images that are keys / mattes etc:
	exclusive_color_key.extend(exclusive_color_saturation)
	exclusive_color_key.extend(exclusive_color_theory)
	exclusive_color_key.extend(exclusive_color_tones)
	exclusive_color_key.extend(exclusive_exterior_nature)
	exclusive_color_key.extend(exclusive_exterior_buildings)
	exclusive_color_key.extend(exclusive_exterior_township1)
	exclusive_color_key.extend(exclusive_exterior_township2)
	exclusive_color_key.extend(exclusive_exterior_vehicles)
	exclusive_color_key.extend(exclusive_interior)
	exclusive_color_key.extend(exclusive_shot_angle)
	exclusive_color_key.extend(exclusive_shot_focus)
	exclusive_color_key.extend(exclusive_shot_framing)
	exclusive_color_key.extend(exclusive_shot_level)
	exclusive_color_key.extend(exclusive_shot_lighting_hard)
	exclusive_color_key.extend(exclusive_shot_lighting_key)
	exclusive_color_key.extend(exclusive_shot_timeofday)
	exclusive_color_key.extend(exclusive_shot_type)
	exclusive_color_key.extend(exclusive_shot_subject)
	exclusive_color_key.extend(exclusive_shot_subject_body)
	exclusive_color_key.extend(exclusive_texture)

	#exterior nature shots cant include any of the following:
	exclusive_exterior_nature.extend(exclusive_exterior_buildings)
	exclusive_exterior_nature.extend(exclusive_exterior_township1)
	exclusive_exterior_nature.extend(exclusive_exterior_township2)
	exclusive_exterior_nature.append("interior")

	# Vehicle shots tend to be out in nature and in town
	# exclusive_exterior_nature.extend(exclusive_exterior_vehicles)

	# all interiors
	exclusive_exterior_nature.extend(exclusive_interior)
	#all shot subjects other than location
	# temp = exclusive_shot_subject[:]
	# temp.remove("shot_subject_location")
	# exclusive_exterior_nature.extend(temp)
	# all shot subjects specific to body
	exclusive_exterior_nature.extend(exclusive_shot_subject_body)
	exclusive_exterior_nature.append("shot_lighting_silhouette")
	exclusive_exterior_nature.append("shot_type_overtheshoulder")

	# all abstract textures 
	exclusive_exterior_nature.extend(exclusive_texture)


	#exterior building shots cant include any of the following:
	exclusive_exterior_buildings.extend(exclusive_exterior_nature)

	# exclusive_exterior_buildings.extend(exclusive_exterior_township1)
	# exclusive_exterior_buildings.extend(exclusive_exterior_township2)
	# exclusive_exterior_buildings.extend(exclusive_exterior_vehicles)

	# all interiors
	exclusive_exterior_buildings.extend(exclusive_interior)
	exclusive_exterior_buildings.append("interior")

	# Any shot types since they require a  subject
	exclusive_exterior_buildings.extend(exclusive_shot_type)
	#all shot subjects other than location
	# temp = exclusive_shot_subject[:]
	# temp.remove("shot_subject_location")
	# exclusive_exterior_buildings.extend(temp)
	# all shot subjects specific to body
	# exclusive_exterior_buildings.extend(exclusive_shot_subject_body)

	exclusive_exterior_buildings.append("shot_lighting_silhouette")
	exclusive_exterior_buildings.append("shot_type_overtheshoulder")


	# all abstract textures 
	exclusive_exterior_buildings.extend(exclusive_texture)


	#exterior township, vehicle shots cant include any of the following:

	# all interiors
	exclusive_exterior_township1.extend(exclusive_interior)
	exclusive_exterior_township2.extend(exclusive_interior)
	exclusive_exterior_vehicles.extend(exclusive_interior)

	exclusive_exterior_township1.append("interior")
	exclusive_exterior_township2.append("interior")
	exclusive_exterior_vehicles.append("interior")

	# Any shot types since they require a  subject
	exclusive_exterior_township1.extend(exclusive_shot_type)
	exclusive_exterior_township2.extend(exclusive_shot_type)
	exclusive_exterior_vehicles.extend(exclusive_shot_type)
	#all shot subjects other than location
	# temp = exclusive_shot_subject[:]
	# temp.remove("shot_subject_location")
	# exclusive_exterior_township1.extend(temp)
	# exclusive_exterior_township2.extend(temp)
	# exclusive_exterior_vehicles.extend(temp)
	# all shot subjects specific to body
	# exclusive_exterior_township1.extend(exclusive_shot_subject_body)
	# exclusive_exterior_township2.extend(exclusive_shot_subject_body)
	# exclusive_exterior_vehicles.extend(exclusive_shot_subject_body)
	# all abstract textures 
	exclusive_exterior_township1.append("shot_lighting_silhouette")
	exclusive_exterior_township2.append("shot_lighting_silhouette")
	exclusive_exterior_vehicles.append("shot_lighting_silhouette")
	exclusive_exterior_township1.append("shot_type_overtheshoulder")
	exclusive_exterior_township2.append("shot_type_overtheshoulder")
	exclusive_exterior_vehicles.append("shot_type_overtheshoulder")

	exclusive_exterior_township1.extend(exclusive_texture)
	exclusive_exterior_township2.extend(exclusive_texture)
	exclusive_exterior_vehicles.extend(exclusive_texture)



	#interior shots cant include any of the following:
	exclusive_interior.extend(exclusive_exterior_nature)
	exclusive_interior.extend(exclusive_exterior_buildings)
	exclusive_interior.extend(exclusive_exterior_township1)
	exclusive_interior.extend(exclusive_exterior_township2)
	exclusive_interior.extend(exclusive_exterior_vehicles)
	exclusive_interior.append("exterior")


	# Any shot types since they require a  subject
	exclusive_interior.extend(exclusive_shot_type)
	# #all shot subjects other than location
	# temp = exclusive_shot_subject[:]
	# temp.remove("shot_subject_location")
	# exclusive_interior.extend(temp)
	# all shot subjects specific to body
	# exclusive_interior.extend(exclusive_shot_subject_body)
	exclusive_interior.append("shot_lighting_silhouette")
	exclusive_interior.append("shot_type_overtheshoulder")

	# all abstract textures 
	exclusive_interior.extend(exclusive_texture)


# individual concepts that need fine tuning

	# shot_subject_text cant be exterior or exterior
	exclusive_shot_subject_text = []
	# exclusive_shot_subject_text.extend(exclusive_exterior_nature)
	# exclusive_shot_subject_text.extend(exclusive_exterior_buildings)
	# exclusive_shot_subject_text.extend(exclusive_exterior_township1)
	# exclusive_shot_subject_text.extend(exclusive_exterior_township2)
	# exclusive_shot_subject_text.extend(exclusive_exterior_vehicles)
	# exclusive_shot_subject_text.extend(exclusive_interior)

	# cant be a shot framing or type since thats a human thing
	exclusive_shot_subject_text.extend(exclusive_shot_framing)
	exclusive_shot_subject_text.extend(exclusive_shot_type)
	# cant be itself, body or textyre
	temp = exclusive_shot_subject[:]
	temp.remove("shot_subject_text")

	exclusive_shot_subject_text.extend(temp)
	exclusive_shot_subject_text.extend(exclusive_shot_subject_body)
	exclusive_shot_subject_text.extend(exclusive_texture)
	exclusive_shot_subject_text.append("shot_lighting_silhouette")

	# a location shot likely doesnt have any opf the following concepts 
	exclusive_shot_subject_location = [
	"shot_subject_location",
	"shot_framing_closeup",
	"shot_framing_extremecloseup",
	"shot_framing_medium",
	]

	exclusive_shot_subject_location.extend(exclusive_shot_subject_body)
	exclusive_shot_subject_location.extend(exclusive_texture)
 	
	exclusive_shot_subject_object = ["shot_subject_object"]
	exclusive_shot_subject_object.extend(exclusive_shot_subject_body)
	exclusive_shot_subject_object.extend(exclusive_texture)


	exclusive_shot_lighting_silhouette = ["shot_lighting_silhouette"]
	exclusive_shot_lighting_silhouette.append("shot_type_portrait") #this doesnt have any silhouttes in it
	# exclusive_shot_lighting_silhouette.extend(exclusive_exterior_nature)
	# exclusive_shot_lighting_silhouette.extend(exclusive_exterior_buildings)
	# exclusive_shot_lighting_silhouette.extend(exclusive_exterior_township1)
	# exclusive_shot_lighting_silhouette.extend(exclusive_exterior_township2)
	# exclusive_shot_lighting_silhouette.extend(exclusive_exterior_vehicles)
	# exclusive_shot_lighting_silhouette.extend(exclusive_interior)
	# exclusive_shot_lighting_silhouette.extend(exclusive_texture)


	# exclusive_shot_type.extend(exclusive_exterior_nature)
	# exclusive_shot_type.extend(exclusive_exterior_buildings)
	# exclusive_shot_type.extend(exclusive_exterior_township1)
	# exclusive_shot_type.extend(exclusive_exterior_township2)
	# exclusive_shot_type.extend(exclusive_exterior_vehicles)
	# exclusive_shot_type.extend(exclusive_interior)
	# exclusive_shot_type.extend(exclusive_texture)



	# portraits cant be over the shoulder
	exclusive_shot_type_overtheshoulder = ["shot_type_overtheshoulder"]
	exclusive_shot_type_overtheshoulder.append("shot_type_portrait")
	exclusive_shot_type_overtheshoulder.append("shot_framing_closeup")
	exclusive_shot_type_overtheshoulder.append("shot_framing_extremecloseup")
	# exclusive_shot_type_overtheshoulder.extend(exclusive_exterior_nature)
	# exclusive_shot_type_overtheshoulder.extend(exclusive_exterior_buildings)
	# exclusive_shot_type_overtheshoulder.extend(exclusive_exterior_township1)
	# exclusive_shot_type_overtheshoulder.extend(exclusive_exterior_township2)
	# exclusive_shot_type_overtheshoulder.extend(exclusive_exterior_vehicles)
	# exclusive_shot_type_overtheshoulder.extend(exclusive_interior)
	temp = exclusive_shot_subject[:]
	temp.remove("shot_subject_person")

	exclusive_shot_type_overtheshoulder.extend(temp)
	exclusive_shot_type_overtheshoulder.extend(exclusive_shot_subject_body)
	exclusive_shot_type_overtheshoulder.extend(exclusive_texture)


	# this might be a bad idea but, lets see:
	# texture is exclusive to all the images since all the images arent specific to a type of texture?
	# exclusive_texture.extend(exclusive_color_key)
	# exclusive_texture.append("exterior")
	# exclusive_texture.append("interior")
	# exclusive_texture.extend(exclusive_color_key)
	# exclusive_texture.extend(exclusive_exterior_buildings)
	# exclusive_texture.extend(exclusive_exterior_township1)
	# exclusive_texture.extend(exclusive_exterior_township2)
	# exclusive_texture.extend(exclusive_exterior_vehicles)
	# exclusive_texture.extend(exclusive_interior)
	# exclusive_texture.extend(exclusive_shot_angle)
	# exclusive_texture.extend(exclusive_shot_focus)
	# exclusive_texture.extend(exclusive_shot_framing)
	# exclusive_texture.extend(exclusive_shot_level)
	# exclusive_texture.extend(exclusive_shot_lighting_hard)
	# exclusive_texture.extend(exclusive_shot_lighting_key)
	# exclusive_texture.append("shot_lighting_silhouette")
	# exclusive_texture.extend(exclusive_shot_timeofday)
	# exclusive_texture.extend(exclusive_shot_type)
	# exclusive_texture.append("shot_type_overtheshoulder")
	# exclusive_texture.extend(exclusive_shot_subject)
	# exclusive_texture.extend(exclusive_shot_subject_body)

	#########
	# make a list of all of our exclusive concepts
	#######

	all_exclusive_concepts = {
	"color_key_" : exclusive_color_key,
	"color_saturation_" : exclusive_color_saturation,
	"color_theory_" : exclusive_color_theory,
	"color_tones_" : exclusive_color_tones,
	"interior_" : exclusive_interior,
	"shot_angle_" : exclusive_shot_angle,
	"shot_focus_" : exclusive_shot_focus,
	"shot_framing" : exclusive_shot_framing,
	"shot_level" : exclusive_shot_level,
	"shot_lighting_hard" : exclusive_shot_lighting_hard,
	"shot_lighting_soft" : exclusive_shot_lighting_hard,
	"shot_lighting_key" : exclusive_shot_lighting_key,
	"shot_timeofday_" : exclusive_shot_timeofday,
	"shot_type_" : exclusive_shot_type,
	"shot_subject_" : exclusive_shot_subject,
	"shot_subject_body_" : exclusive_shot_subject_body,
	"texture_" : exclusive_texture,

	# individual concepts
	"exterior_beach" : exclusive_exterior_nature,
	"exterior_canyon" : exclusive_exterior_nature,
	"exterior_cave" : exclusive_exterior_nature,
	"exterior_desert" : exclusive_exterior_nature,
	"exterior_forest" : exclusive_exterior_nature,
	"exterior_glacier" : exclusive_exterior_nature,
	"exterior_lake" : exclusive_exterior_nature,
	"exterior_mountains" : exclusive_exterior_nature,
	"exterior_ocean" : exclusive_exterior_nature,
	"exterior_plains" : exclusive_exterior_nature,
	"exterior_polar" : exclusive_exterior_nature,
	"exterior_river" : exclusive_exterior_nature,
	"exterior_sky" : exclusive_exterior_nature,
	"exterior_space" : exclusive_exterior_nature,
	"exterior_wetlands" : exclusive_exterior_nature,

	"exterior_airport" : exclusive_exterior_buildings,
	"exterior_apartment" : exclusive_exterior_buildings,
	"exterior_auto_body" : exclusive_exterior_buildings,
	"exterior_bridge" : exclusive_exterior_buildings,
	"exterior_bus_stop" : exclusive_exterior_buildings,
	"exterior_castle" : exclusive_exterior_buildings,
	"exterior_cathedral" : exclusive_exterior_buildings,
	"exterior_church" : exclusive_exterior_buildings,
	"exterior_farm" : exclusive_exterior_buildings,
	"exterior_hospital" : exclusive_exterior_buildings,
	"exterior_house" : exclusive_exterior_buildings,
	"exterior_industrial" : exclusive_exterior_buildings,
	"exterior_library" : exclusive_exterior_buildings,
	"exterior_mall" : exclusive_exterior_buildings,
	"exterior_mansion" : exclusive_exterior_buildings,
	"exterior_monastery" : exclusive_exterior_buildings,
	"exterior_mosque" : exclusive_exterior_buildings,
	"exterior_office" : exclusive_exterior_buildings,
	"exterior_palace" : exclusive_exterior_buildings,
	"exterior_parkinglot" : exclusive_exterior_buildings,
	"exterior_pier" : exclusive_exterior_buildings,
	"exterior_port" : exclusive_exterior_buildings,
	"exterior_restaurant" : exclusive_exterior_buildings,
	"exterior_ruins" : exclusive_exterior_buildings,
	"exterior_school" : exclusive_exterior_buildings,
	"exterior_skyscraper" : exclusive_exterior_buildings,
	"exterior_stadium" : exclusive_exterior_buildings,
	"exterior_station_gas" : exclusive_exterior_buildings,
	"exterior_station_subway" : exclusive_exterior_buildings,
	"exterior_station_train" : exclusive_exterior_buildings,
	"exterior_store" : exclusive_exterior_buildings,
	"exterior_synagogue" : exclusive_exterior_buildings,
	"exterior_temple" : exclusive_exterior_buildings,
	"exterior_theater" : exclusive_exterior_buildings,
	"exterior_tunnel" : exclusive_exterior_buildings,
	"exterior_warehouse" : exclusive_exterior_buildings,


	"exterior_city" : exclusive_exterior_township1,
	"exterior_suburb" : exclusive_exterior_township1,
	"exterior_town" : exclusive_exterior_township1,

	"exterior_park" : exclusive_exterior_township2, 
	"exterior_playground" : exclusive_exterior_township2, 
	"exterior_road" : exclusive_exterior_township2, 
	"exterior_sidewalk" : exclusive_exterior_township2, 

	"exterior_airplane": exclusive_exterior_vehicles,
	"exterior_bicycle": exclusive_exterior_vehicles,
	"exterior_boat": exclusive_exterior_vehicles,
	"exterior_bus": exclusive_exterior_vehicles,
	"exterior_car": exclusive_exterior_vehicles,
	"exterior_helicopter": exclusive_exterior_vehicles,
	"exterior_motorcycle": exclusive_exterior_vehicles,
	"exterior_spacecraft": exclusive_exterior_vehicles,
	"exterior_train": exclusive_exterior_vehicles,
	"exterior_truck": exclusive_exterior_vehicles,


	"shot_subject_text" : exclusive_shot_subject_text,
	"shot_subject_location" : exclusive_shot_subject_location,
	"shot_subject_object" : exclusive_shot_subject_object,
	"shot_lighting_silhouette" : exclusive_shot_lighting_silhouette,
	"shot_type_overtheshoulder" : exclusive_shot_type_overtheshoulder,

	"shot_type_portrait" : ["shot_type_overtheshoulder", "shot_lighting_silhouette"],
	"shot_framing_closeup" : ["shot_type_overtheshoulder"],
	"shot_framing_extremecloseup" : ["shot_type_overtheshoulder", "shot_lighting_silhouette"],
	}

	# print(all_exclusive_concepts)

	# recurse through our image directory and run inference on each image
	for subdir, dirs, files in os.walk(args.imagedir):
		for file in files:
			#print os.path.join(subdir, file)
			filepath = subdir + os.sep + file

			if filepath.endswith(".jpg"):
				all_files.append(filepath)


	all_files.sort()

	#do we shuffle our files?
	if args.random == True:
		random.shuffle(all_files)

	#do we limit our file count so we can do a test run?
	if args.limit is not 0:
		all_files = all_files[:args.limit]


	for filepath in all_files:

		filename = os.path.basename( filepath )
		file_concept = os.path.basename ( os.path.dirname( filepath ) )

		# print("label for: " + filepath + " is " + file_concept)

		#print os.path.join(subdir, file)
		if filepath.endswith(".jpg"):

			#make a dictionary that contains a valye for every label as key for easy introspection
			# set all values to unknown for to start
			file_label_value = []

			for label in labels:
				file_label_value.append(unknown)

			# mark all exclusive concepts as negative
			for key in all_exclusive_concepts.keys():
				exclusive_concept_list_for_key = all_exclusive_concepts[key]
				if key in file_concept:
					for exclusive_concept in exclusive_concept_list_for_key:
						index = labels.index(exclusive_concept)
						file_label_value[index] = negative

			# # mark any specific interior or exterior concept as true for the  interior or exterior master label
			# # and ensure all opposites are 0 - (and exterior anything cant be an interior anything, and vice versa) 
			if 'exterior' in file_concept:
				index = labels.index('exterior')
				file_label_value[index] = positive

				index = labels.index('shot_subject_location')
				file_label_value[index] = positive

				#if we have an exterior mark all interiors and negative
				for label in labels:
					if 'interior' in label:
						index = labels.index(label)
						file_label_value[index] = negative

			if 'interior' in file_concept:
				index = labels.index('interior')
				file_label_value[index] = positive

				index = labels.index('shot_subject_location')
				file_label_value[index] = positive

				#if we have an interior mark all exteriors and negative
				for label in labels:
					if 'exterior' in label:
						index = labels.index(label)
						file_label_value[index] = negative

			# if our file concept is shot_subject_person, ensure we mark our shot_subject categories appropriately
			if 'shot_subject_person' in file_concept:

				# mark all shot subjects negative
				for label in labels:
					if 'shot_subject_' in label:
						index = labels.index(label)
						file_label_value[index] = negative

				# mark shot_subject_body positive
				index = labels.index('shot_subject_person')
				file_label_value[index] = positive


			# our parent folder is our label, clearly we are known
			index = labels.index(file_concept)
			file_label_value[index] = positive

			# add our new calculated labels to the all label
			all_files_label_values.append(file_label_value)

			# for i in range(len(labels)):
			# 	print(labels[i] + " : " + str(file_label_value[i]))


	#write header
	header = []
	header.append('filepath')
	header.extend(labels)
	writer.writerow(header)

	for i in range( len(all_files) ):
		csv_row= []
		#filepath
		csv_row.append( all_files[i] )

		# dont nest, but extend csv row with contents of label value
		label_values_for_file = all_files_label_values[i]
		csv_row.extend(label_values_for_file)

		writer.writerow(csv_row)





