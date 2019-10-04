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
"texture_zigzagged",
]

################
# NOTE THAT NOT APPLICABLE LABELS / CONCEPTS MUST EXACTLY MATCH ON DISK FOLDER NAMES
# NOT APPLICABLE CONCEPTS ARE MARKED AS FALSE FOR ALL LABELS EXCEPT THEIR OWN
################

not_applicable_key = None
not_applicable_concepts = None

auto_label.auto_label(args, exclusive_concepts, exclusive_concepts, not_applicable_key, not_applicable_concepts)


