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

# individual concepts that need fine tuning

	exclusive_shot_angle_aerial = ["shot_angle_aerial", "shot_framing_closeup", "shot_framing_extremecloseup", "shot_framing_long", "shot_framing_medium", "shot_subject_animal", "shot_subject_person", "shot_subject_person_body", "shot_subject_person_face", "shot_subject_person_feet", "shot_subject_person_hands", "shot_type_overtheshoulder", "shot_type_master", "shot_type_portrait", "shot_type_twoshot" ]

	# shot_subject_text cant be exterior or exterior
	exclusive_shot_subject_text = []

	# cant be a shot framing or type since thats a human thing
	exclusive_shot_subject_text.extend(exclusive_shot_framing)
	exclusive_shot_subject_text.extend(exclusive_shot_type)
	# cant be itself, body or textyre
	temp = exclusive_shot_subject[:]
	temp.remove("shot_subject_text")

	exclusive_shot_subject_text.extend(temp)
	exclusive_shot_subject_text.extend(exclusive_shot_subject_body)
	exclusive_shot_subject_text.append("shot_lighting_silhouette")

	# a location shot likely doesnt have any opf the following concepts 
	exclusive_shot_subject_location = [
	"shot_subject_location",
	"shot_framing_closeup",
	"shot_framing_extremecloseup",
	"shot_framing_medium",
	]
	exclusive_shot_subject_location.extend(exclusive_shot_subject_body)

 	
	exclusive_shot_subject_object = ["shot_subject_object"]
	exclusive_shot_subject_object.extend(exclusive_shot_subject_body)

	exclusive_shot_lighting_silhouette = ["shot_lighting_silhouette"]
	exclusive_shot_lighting_silhouette.append("shot_type_portrait") #this doesnt have any silhouttes in it

	# portraits cant be over the shoulder
	exclusive_shot_type_overtheshoulder = ["shot_type_overtheshoulder"]
	exclusive_shot_type_overtheshoulder.append("shot_type_portrait")
	exclusive_shot_type_overtheshoulder.append("shot_framing_closeup")
	exclusive_shot_type_overtheshoulder.append("shot_framing_extremecloseup")
	temp = exclusive_shot_subject[:]
	temp.remove("shot_subject_person")

	exclusive_shot_type_overtheshoulder.extend(temp)
	exclusive_shot_type_overtheshoulder.extend(exclusive_shot_subject_body)


	#########
	# make a list of all of our exclusive concepts
	#######

	all_exclusive_concepts = {
	
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

	"shot_angle_aerial" : exclusive_shot_angle_aerial,
	
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





