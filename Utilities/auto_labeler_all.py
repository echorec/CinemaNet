import os 
import csv   
import argparse
import random
import math
import time
import json
import auto_label
import sys

parser = argparse.ArgumentParser(description='Use a folder of ML model classifiers to label a local unlabeled data set')
parser.add_argument('-i', '--imagedir', type=str, help="folder containing unlabeled images to be labeled", default="./images", required=True)
parser.add_argument('-o', '--output', type=str, help="destination folder for CSV files", required=True)
parser.add_argument('-pre', '--prefix', type=str, help="image url prefix, useful for adding a cloud storage provider URLs to the CSV path", default="", required=False)
parser.add_argument('-l', '--limit', type=int, help="limit the number of images we label - useful for testing", default="1000000000000", required=False)
parser.add_argument('-r', '--random', type=bool, help="limit the number of images we label - useful for testing", default=False, required=False)

args = parser.parse_args()


def label(label):
	print("")
	print("")
	print("Labelling " + label)
	command = "python auto_labeler_" + label + ".py"
	command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + label + ".csv" 
	print(command)
	os.system(command)
	print("")
	print("")

label("color_key")
label("color_saturation")
label("color_theory")
label("color_tones")
label("shot_angle")
label("shot_focus")
label("shot_framing")
label("shot_level")
label("shot_lighting")
label("shot_location")
label("shot_subject")
label("shot_timeofday")
label("shot_type")
label("texture")



# print("Labelling color_key")
# command = "python auto_labeler_color_key.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "color_key.csv" 
# print(command)
# os.system(command)


# print("Labelling color_saturation")
# command = "python auto_labeler_color_saturation.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "color_saturation.csv" 
# print(command)
# os.system(command)

# print("Labelling color_theory")
# command = "python auto_labeler_color_theory.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "color_theory.csv" 
# print(command)
# os.system(command)

# print("Labelling color_tones")
# command = "python auto_labeler_color_tones.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "color_tones.csv" 
# print(command)
# os.system(command)

# print("Labelling shot_angle")
# command = "python auto_labeler_shot_angle.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "shot_angle.csv" 
# print(command)
# os.system(command)

# print("Labelling shot_focus")
# command = "python auto_labeler_shot_focus.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "shot_focus.csv" 
# print(command)
# os.system(command)

# print("Labelling shot_framing")
# command = "python auto_labeler_shot_framing.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "shot_framing.csv" 
# print(command)
# os.system(command)

# print("Labelling shot_level")
# command = "python auto_labeler_shot_level.py"
# command = command + " -i=\"" + args.imagedir + "\" -o=" + args.output + "shot_level.csv" 
# print(command)
# os.system(command)
