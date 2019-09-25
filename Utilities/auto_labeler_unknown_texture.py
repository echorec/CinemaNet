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


	all_exclusive_concepts = {
	
	"texture_" : exclusive_texture,

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





