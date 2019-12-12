import os 
import csv   
import argparse
import random
import string

parser = argparse.ArgumentParser(description='Use a folder of csv data set declarations for google collab and create tasks appropriate for Label Studio')
parser.add_argument('-i', '--cvsdir', type=str, help='folder containing csv data for google collab', required=True)
parser.add_argument('-o', '--outputdir', type=str, help="output folder for UI markup text files", default="./LabelUI", required=True)
parser.add_argument('-p', '--prefix', type=str, help="output folder for UI markup text files", default="https://storage.googleapis.com/synopsis_cinemanet/Synopsis_Model_All_Concepts/", required=False)

args = parser.parse_args()

# load our models into our models array
dir_path = os.getcwd()

csvs_dir = os.path.normpath( os.path.join(dir_path, args.cvsdir) )

print('Loading csvs from: ' + csvs_dir)

csvs = []

csvfiles = os.listdir(csvs_dir)
csvfiles.sort()


for filename in csvfiles:
	if filename.endswith('.csv'):	
		csv_path = (os.path.join(csvs_dir, filename))

		print('processing' + filename)

		output_ui_file = (os.path.join(args.outputdir, filename.replace(".csv", "") + "_labelstudio_tasks.csv" ))

		with  open(csv_path, 'rb') as source,  open(output_ui_file, "w") as destination:

			csvreader = csv.reader(source)
			csvwriter = csv.writer(destination)

			for row in csvreader:
				if row[0] == "filepath":
					row[0] = "image"

				else:
					row[0] = args.prefix + row[0]

				csvwriter.writerow(row)

			source.close()					
			destination.close()					
			print('wrote ' + output_ui_file)


						      
