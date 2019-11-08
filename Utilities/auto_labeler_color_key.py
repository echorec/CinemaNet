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

# list of exclusive concepts groups:
exclusive_concepts = [
"color_key_blue",
"color_key_green",
"color_key_luma",
"color_key_matte",
]


################
# NOTE THAT NOT APPLICABLE LABELS / CONCEPTS MUST EXACTLY MATCH ON DISK FOLDER NAMES
# NOT APPLICABLE CONCEPTS ARE MARKED AS FALSE FOR ALL LABELS EXCEPT THEIR OWN
################


# unsure if a key is applicable.
# we could just mark 0 in all of the above keys and be done with it?
# but not applicable is a good signal tho too?
not_applicable_key = "color_key_na"

not_applicable_concepts = [
"color_saturation",
"color_theory",
"color_tones",

# NOTE: We had WAY too many images for the NA - which made the model way less confident for any actual green / blue screen images
# "shot_angle",
# "shot_focus",
# "shot_framing",
# "shot_level",
# "shot_lighting",
# "shot_location",
# "shot_subject",
# "shot_timeofday",
# "shot_type",
"texture",
]

auto_label.auto_label(args, exclusive_concepts, exclusive_concepts, not_applicable_key, not_applicable_concepts)


