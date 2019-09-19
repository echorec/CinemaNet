import os 
import csv   
import argparse
import random
import math
import time
from shutil import copyfile

import sklearn
from sklearn.model_selection import StratifiedKFold
# from sklearn.model_selection import KFold # import KFold
# from sklearn.model_selection import GroupKFold # import KFold
# from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser(description='Split a folder structure of images via KFold for cross validation, exporting CVSs for each fold')
parser.add_argument('-s', '--splits', type=int, help='stratification count', required=True)
parser.add_argument('-d', '--datasetdir', type=str, help='folder containing subfolders as labels and contents of labels as data', required=True)
parser.add_argument('-o', '--output', type=str, help="destination folder for split CSV or fodler structure", default="./labels", required=True)

args = parser.parse_args()


# load our models into our models array
dir_path = os.getcwd()

dataset_path = os.path.normpath( args.datasetdir )
print('Loading Dataset from: ' + dataset_path)

labels = []
imagepaths = []

for subdir, dirs, files in os.walk(dataset_path):

	files.sort()

	for filename in files:

		if filename.endswith('.jpg'):	
			image_path = os.path.join( os.path.join(dataset_path, subdir), filename)

			if image_path:
				imagepaths.append(image_path)

				label = os.path.basename( os.path.dirname(image_path) )
				labels.append(label)


print("Labels:")
print(len(labels))
print("Num Images:")
print(len(imagepaths))

#paths_train, paths_test, labels_train, labels_test  = train_test_split( imagepaths, labels, test_size=0.01, random_state=42, stratify=labels)
# kf = GroupKFold(n_splits=10)
skf = StratifiedKFold(n_splits=args.splits, shuffle=True, random_state=42)

count = 0
for train_index, test_index in skf.split(imagepaths, labels):

#	if count < 2:

	print("Num images in stratified fold")
	print(len(test_index))

	fold_dir = os.path.join(os.path.join(args.output, "FOLD_"+str(count)))

	if not os.path.exists(fold_dir):	
		try:
			print("creating", fold_dir)
		 	os.mkdir(fold_dir)
		except OSError:
			print ("Creation of the directory %s failed" % fold_dir)

	for index in test_index:
		src = imagepaths[index]
		filename = os.path.basename( src )
		dirname = os.path.basename ( os.path.dirname( src ) )

		dest_folder = os.path.join(fold_dir, dirname)
		dest = os.path.join( dest_folder, filename)
		print("copy ", src, " to ", dest)

		if not os.path.exists(dest_folder):
			try:
				print("creating", dest_folder)
				os.mkdir(dest_folder)
			except OSError:
			    print ("Creation of the directory %s failed" % dest_folder)

		copyfile(src, dest)

	count = count + 1

	
	# train_splits.append(imagepaths[test_index])

# print("Num Test Splits")

# print(len(train_splits))

# print("Num Paths in a Test Split")

# print(len(train_splits[0]))

# print("Train Split")
# print(len(paths_train))
# print(len(labels_train))

# print(len(test_index))
# print(len(test_index[0]))
# print(test_index)
# for train_index, test_index in kf.split(imagepaths, y=labels, groups=None):
# 	print("Num Train:", len(train_index))
# 	print("Num Test:", len(test_index))
# 	print("TRAIN:", train_index, "TEST:", test_index)

