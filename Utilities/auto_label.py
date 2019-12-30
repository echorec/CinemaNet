
import os 
import csv   
import argparse
import random
import math
import time
import json

# recurse through our image directory and determine the known positive label (1) known negative labels (0), and unknown labels (-1)
positive = "1"
negative = "0"
unknown = "-1"


def auto_label(args, labels, exclusive_concepts, not_applicable_key, not_applicable_concepts, label_closure=None):

	# put out initial labels into alpha-betical order prior to doing shit.
	# n/a gets appended at the end
	labels.sort()

	# if exclusive_concepts != None:
	# 	exclusive_concepts.sort()
	
	if not_applicable_concepts != None:
		not_applicable_concepts.sort()

	# ensure our not on disk not applicable key is added to all labels
	if not_applicable_concepts != None and not_applicable_key != None:
		labels.append(not_applicable_key)

	if not_applicable_concepts == None:
		not_applicable_concepts = []

	print(labels)

	# make a dictionary whose key is the file concept string and contains paths for every file 
	concept_files = {}

	for label in labels:
		concept_files[label] = []

	# all valid files we will label
	all_files = []

	# for every file, an array of [1, 0, -1] to represent the label for that index's known state.
	all_files_label_values = []

	with open(args.output, 'wb') as writer:

		writer = csv.writer(writer)

		# recurse through our image directory and run inference on each image
		for subdir, dirs, files in os.walk(args.imagedir):
			for file in files:
				filepath = subdir + os.sep + file

				# we only care about the paths relative to the data set root, which is 
				filepath = filepath.replace(args.imagedir, "")

				file_concept = os.path.basename ( os.path.dirname( filepath ) )

				if ( filepath.endswith(".jpg") or filepath.endswith(".jpeg") ) and ( filter(lambda x: x in file_concept, labels)  ):

					concept_files[file_concept].append(filepath)

				elif ( filepath.endswith(".jpg") or filepath.endswith(".jpeg") ) and ( filter(lambda x: x in file_concept, not_applicable_concepts)  ):

					concept_files[not_applicable_key].append(filepath)



		# we should prune our NA concepts to ensure they roughly match the number of other concepts, otherwise our data set is unbalanced
		if not_applicable_key != None:
			na_examples = concept_files[not_applicable_key]
			naExampleCount = len(na_examples)

			maxConceptExamples = 0
			for key in concept_files:
				if key != not_applicable_key:
					conceptCount = len(concept_files[key])
					maxConceptExamples = max(maxConceptExamples, conceptCount)

			# if we have more NA examples than class concept examples, andomly shuffle our NA examples and clip the array to match the larges class size
			if naExampleCount > maxConceptExamples:
				print("NA examples larger than concept size, shuffling then clipping")
				random.shuffle(na_examples)
				na_examples = na_examples[:maxConceptExamples]
				concept_files[not_applicable_key] = na_examples

		# unroll all of our concept_file arrays into a flat array of all files
		for key in concept_files:
			all_files.extend( concept_files[key])


		# directory traversal is in inode order not alpabetical
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


			#print os.path.join(subdir, file)

			#make a list that contains a value (positibe, negative or unknown) for every label for the file
			file_label_value = []

			# set all labels to unknown for to start
			# or negative for NA
			for label in labels:
				if label == not_applicable_key:
					file_label_value.append(negative)
				else:
					file_label_value.append(unknown)

			# mark all exclusive concepts as negative
			
			#flat list of exclusive concepts:
			if isinstance(exclusive_concepts, list):
				for exclusive_concept in exclusive_concepts:
					index = labels.index(exclusive_concept)
					file_label_value[index] = negative

			#dictionary of paired exclusive concepts to specific keys
			elif isinstance( exclusive_concepts, dict):
				for key in exclusive_concepts.keys():
					exclusive_concept_list_for_key = exclusive_concepts[key]
					if key in file_concept:
						for exclusive_concept in exclusive_concept_list_for_key:
							index = labels.index(exclusive_concept)
							file_label_value[index] = negative


			# if our file is in folder thats not applicable, zero our all labels and mark the na label as true
			if not_applicable_concepts != None and not_applicable_key != None:
				for not_applicable_concept in not_applicable_concepts:


					# note our NA concepts can be wildcards / partial text matching
					if not_applicable_concept in file_concept:
	
						#mark all known labels as negative
						for i in range( len(labels) ):
							file_label_value[i] = negative

						index = labels.index(not_applicable_key)
						file_label_value[index] = positive

			# Call our label closure if we have one
			if label_closure != None:
				file_label_value =label_closure(file_concept, labels, file_label_value )


			if file_concept in labels:
				# our parent folder is our label, clearly we are known
				index = labels.index(file_concept)
				file_label_value[index] = positive

			# add our new calculated labels to the all label
			all_files_label_values.append(file_label_value)



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

