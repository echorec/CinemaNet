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


	#exterior nature shots cant include any of the following:
	exclusive_exterior_nature.extend(exclusive_exterior_buildings)
	exclusive_exterior_nature.extend(exclusive_exterior_township1)
	exclusive_exterior_nature.extend(exclusive_exterior_township2)
	exclusive_exterior_nature.extend(exclusive_exterior_vehicles)
	exclusive_exterior_nature.extend(exclusive_interior)
	exclusive_exterior_nature.append("interior")

	#exterior building shots cant include any of the following:
	exclusive_exterior_buildings.extend(exclusive_exterior_nature)
	exclusive_exterior_buildings.extend(exclusive_exterior_township1)
	exclusive_exterior_buildings.extend(exclusive_exterior_township2)
	exclusive_exterior_buildings.extend(exclusive_exterior_vehicles)
	exclusive_exterior_buildings.extend(exclusive_interior)
	exclusive_exterior_buildings.append("interior")


	exclusive_exterior_township1.extend(exclusive_exterior_nature)
	exclusive_exterior_township1.extend(exclusive_exterior_buildings)
	exclusive_exterior_township1.extend(exclusive_exterior_township2)
	exclusive_exterior_township1.extend(exclusive_exterior_vehicles)
	exclusive_exterior_township1.extend(exclusive_interior)
	exclusive_exterior_township1.append("interior")


	exclusive_exterior_township2.extend(exclusive_exterior_nature)
	exclusive_exterior_township2.extend(exclusive_exterior_buildings)
	exclusive_exterior_township2.extend(exclusive_exterior_township1)
	exclusive_exterior_township2.extend(exclusive_exterior_vehicles)
	exclusive_exterior_township2.extend(exclusive_interior)
	exclusive_exterior_township2.append("interior")

	exclusive_exterior_vehicles.extend(exclusive_exterior_nature)
	exclusive_exterior_vehicles.extend(exclusive_exterior_buildings)
	exclusive_exterior_vehicles.extend(exclusive_exterior_township1)
	exclusive_exterior_vehicles.extend(exclusive_exterior_township2)
	exclusive_exterior_vehicles.extend(exclusive_interior)
	exclusive_exterior_vehicles.append("interior")

	#interior shots cant include any of the following:
	exclusive_interior.extend(exclusive_exterior_nature)
	exclusive_interior.extend(exclusive_exterior_buildings)
	exclusive_interior.extend(exclusive_exterior_township1)
	exclusive_interior.extend(exclusive_exterior_township2)
	exclusive_interior.extend(exclusive_exterior_vehicles)
	exclusive_interior.append("exterior")

	all_exclusive_concepts = {
	
	"interior_" : exclusive_interior,


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


				#if we have an exterior mark all interiors and negative
				for label in labels:
					if 'interior' in label:
						index = labels.index(label)
						file_label_value[index] = negative

			if 'interior' in file_concept:
				index = labels.index('interior')
				file_label_value[index] = positive

				# index = labels.index('shot_subject_location')
				# file_label_value[index] = positive

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





