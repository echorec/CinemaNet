import os 
import csv   
import argparse
import random
import string

parser = argparse.ArgumentParser(description='Use a folder of labels text files and create markup for label studio UI based on the concepts in each label ')
parser.add_argument('-i', '--labeldir', type=str, help='folder containing label text files', required=True)
parser.add_argument('-o', '--outputdir', type=str, help="output folder for UI markup text files", default="./LabelUI", required=True)

args = parser.parse_args()

# load our models into our models array
dir_path = os.getcwd()

labels_path = os.path.normpath( os.path.join(dir_path, args.labeldir) )

print('Loading labels from: ' + labels_path)

labels = []

labelfiles = os.listdir(labels_path)
labelfiles.sort()

for filename in labelfiles:
	if filename.endswith('.txt'):	
		label_path = (os.path.join(labels_path, filename))

		output_ui_file = (os.path.join(args.outputdir, filename.replace(".txt", "") + "_labestudio_ui.txt" ))

		with open(label_path, 'r') as label_file:
			labels = label_file.read()
			labels = labels.split(", ")

			with open(output_ui_file, 'wb') as writer:

				header = 	"""
<View>
	<Image name="img" value="$image" maxWidth="400" width="75%"></Image>
	<Header value="Please check all applicable concepts in the image - refer to help for clarification on the concepts"></Header>
	<View style="width:100%">
		<Choices choice="multiple" name="label_studio_ui" toName="img" showInline="false">

"""

				footer = """
		</Choices>
	</View>
</View>
"""


				choices = []
				for label in labels:
					label_without_first_two_components_cleaned_up = " ".join( label.split("_")[2:])

					label_without_first_two_components_cleaned_up = label_without_first_two_components_cleaned_up.capitalize()

					if label_without_first_two_components_cleaned_up == "Na":
						label_without_first_two_components_cleaned_up = "Not Applicable - no concepts visible"
					label_UI_text = "		<Choice value=\"{}\" alias=\"{}\"></Choice>".format(label_without_first_two_components_cleaned_up, label)
					choices.append(label_UI_text)

				writer.write(header)


				writer.write("\n".join(choices))

				writer.write(footer)
				writer.close()					





						      
