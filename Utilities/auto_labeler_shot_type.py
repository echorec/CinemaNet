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
"shot_type_portrait",
"shot_type_twoshot",
"shot_type_master",
"shot_type_overtheshoulder",
]

# MANUALLY GOING THROUGH THESE FOLDERS FOUND A FEW OUTLIERS AND ALSO THAT THESE CONCEPTS ARE ALL MUTUALLY EXCLUSIVE AS OF THIS COMMENT

# list of exclusive concepts groups:
# exclusive_concepts = {
# # portrait cant contain two master of OTS
# "shot_type_portrait" : ["shot_type_portrait", "shot_type_twoshot", "shot_type_master", "shot_type_overtheshoulder"],

# # two could be OTS, so remove it
# "shot_type_twoshot" : ["shot_type_portrait", "shot_type_twoshot", "shot_type_master", "shot_type_overtheshoulder"],

# #master could be OTS (is that true, I guess so?)
# "shot_type_master" : ["shot_type_portrait", "shot_type_twoshot", "shot_type_master"],

# #OTS can't be portrait and no examples in two shot
# "shot_type_overtheshoulder" : [ "shot_type_overtheshoulder",  "shot_type_portrait", "shot_type_twoshot" ]
# }


################
# NOTE THAT NOT APPLICABLE LABELS / CONCEPTS MUST EXACTLY MATCH ON DISK FOLDER NAMES
# NOT APPLICABLE CONCEPTS ARE MARKED AS FALSE FOR ALL LABELS EXCEPT THEIR OWN
################


# unsure if a key is applicable.
# we could just mark 0 in all of the above keys and be done with it?
# but not applicable is a good signal tho too?
not_applicable_key = "shot_type_na"

not_applicable_concepts = [
"texture"
]

auto_label.auto_label(args, labels, labels, not_applicable_key, not_applicable_concepts)


