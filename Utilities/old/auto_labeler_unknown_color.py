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
]

# list of exclusive concepts groups:
exclusive_color_key = [
"color_key_blue",
"color_key_green",
"color_key_luma",
"color_key_matte",
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
	

	all_exclusive_concepts = {
	"color_key_" : exclusive_color_key,
	"color_saturation_" : exclusive_color_saturation,
	"color_theory_" : exclusive_color_theory,
	"color_tones_" : exclusive_color_tones,
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





