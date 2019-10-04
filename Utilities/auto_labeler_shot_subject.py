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
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",
"shot_subject_text",
]

exclusive_shot_subject_animal = [
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",
"shot_subject_text",
]

exclusive_shot_subject_location = [
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",
"shot_subject_text",
]

exclusive_shot_subject_object = [
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",
"shot_subject_text",
]

exclusive_shot_subject_person = [
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",

# these are manualy flipped positive in auto_label which is lame 
# todo: FIX so we can do that here

# "shot_subject_person_body",
# "shot_subject_person_face",
# "shot_subject_person_feet",
# "shot_subject_person_hands",

"shot_subject_text",
]


exclusive_shot_subject_person_body = [
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",

# person is manually flipped on for body, face, feet, hands
# but each one is exclusive to themsleves
# "shot_subject_person",
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",

"shot_subject_text",
]

exclusive_shot_subject_text = [
"shot_subject_animal",
"shot_subject_location",
"shot_subject_object",
"shot_subject_person",
"shot_subject_person_body",
"shot_subject_person_face",
"shot_subject_person_feet",
"shot_subject_person_hands",
"shot_subject_text",
]


# list of exclusive concepts groups:
exclusive_concepts = {
"shot_subject_animal" : exclusive_shot_subject_animal,
"shot_subject_location" : exclusive_shot_subject_location,
"shot_subject_object" : exclusive_shot_subject_object,
"shot_subject_person" : exclusive_shot_subject_person,
"shot_subject_person_body" : exclusive_shot_subject_person_body,
"shot_subject_person_face" : exclusive_shot_subject_person_body,
"shot_subject_person_feet" : exclusive_shot_subject_person_body,
"shot_subject_person_hands" : exclusive_shot_subject_person_body,
"shot_subject_text" : exclusive_shot_subject_text,

}


################
# NOTE THAT NOT APPLICABLE LABELS / CONCEPTS MUST EXACTLY MATCH ON DISK FOLDER NAMES
# NOT APPLICABLE CONCEPTS ARE MARKED AS FALSE FOR ALL LABELS EXCEPT THEIR OWN
################


# unsure if a key is applicable.
# we could just mark 0 in all of the above keys and be done with it?
# but not applicable is a good signal tho too?
not_applicable_key = "shot_subject_na"

not_applicable_concepts = [
"texture"
]

auto_label.auto_label(args, labels, exclusive_concepts, not_applicable_key, not_applicable_concepts)


