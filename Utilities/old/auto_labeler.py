import os 
import csv   
import argparse
import PIL.Image
import coremltools
import random
import math
import time
import gc
from Foundation import NSAutoreleasePool

parser = argparse.ArgumentParser(description='Use a folder of ML model classifiers to label a local unlabeled data set')
parser.add_argument('-m', '--modeldir', type=str, help='folder containing core ml models to use as labelers. Each image to label will be run through each model', default='../Models/Classifiers/Cleaned/', required=False)
parser.add_argument('-i', '--imagedir', type=str, help="folder containing unlabeled images to be labeled", default="./images", required=True)
parser.add_argument('-o', '--output', type=str, help="destination for labeled file containing multi labels", default="./labels", required=False)
parser.add_argument('-t', '--type', type=str, help="csv or html?", default="csv", required=False)
parser.add_argument('-pre', '--prefix', type=str, help="image url prefix, useful for adding a cloud storage provider URLs to the CSV path", default="", required=False)
parser.add_argument('-l', '--limit', type=int, help="limit the number of images we label - useful for testing", default="1000000000000", required=False)
parser.add_argument('-r', '--random', type=bool, help="limit the number of images we label - useful for testing", default=False, required=False)
parser.add_argument('-p', '--probabilities', type=bool, help="report probabilities rather than predicted class label (html only)", default=False, required=False)
parser.add_argument('-c', '--confidence', type=int, help="the confidence score we need to meet or exceed to apply a class label to an image", default=75, required=False)
parser.add_argument('-s', '--randomseed', type=int, help="random seed for deterministic runs", default=42, required=False)

args = parser.parse_args()

confidence = args.confidence / 100.0

start = time.time()

# load our models into our models array
dir_path = os.getcwd()

models_path = os.path.normpath( os.path.join(dir_path, args.modeldir) )

print('Loading Models from: ' + models_path)

models = []

modelfiles = os.listdir(models_path)
modelfiles.sort()

for filename in modelfiles:
	if filename.endswith('.mlmodel'):	
		model_path = (os.path.join(models_path, filename))

		if model_path:
			model = coremltools.models.MLModel(model_path)

			if model:
				print('Loaded model ' + filename)
				models.append(model)
			else:
				print('Unable to load model at ' + model_path)
	else:
		continue


end = time.time()

modeltime = end - start

print("")
print("Loading models took " + str(modeltime) + " seconds")
print("")

Height = 224 # use the correct input image height 
Width = 224 # use the correct input image width

#https://github.com/python-pillow/Pillow/issues/2019
def load_image(path, resize_to=None):

	try:
		# img = PIL.Image.open(path)
		# #verify apparently breaks the image!?
		# # img.verify()
		with open(path, 'rb') as f:
		    img = PIL.Image.open(f)
		    # We need to consume the whole file inside the `with` statement
		    img.load()


	except Exception:
		print('Unable to load image' + path)
		return [None, f]

	if resize_to is not None:
		try:
			img = img.resize(resize_to, PIL.Image.ANTIALIAS)
		except Exception:
			print('Unable to resize image' + path)
			return [None, f]

	# ensure we pass our image as RGB - some images might be single channel or RGBA
	if img.mode != 'RGB':
		try:
			img = img.convert(mode='RGB')
		except Exception:
			print('Unable to convert image to RGB' + path)
			return [None, f]

	return [img, f]

def html_header(): 
	html_header = """
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">

	<html>

		<head>

		<title>Synopsis Data Set Auto Labeler Output</title>
		<style>

		body {
		  font-family: Arial, Sans-serif;
		  font-size: 10pt;
		}
		.masonry-layout {
		  column-count: 3;
		  column-gap: 0;
		}
		.masonry-layout__panel {
		  break-inside: avoid;
		  margin:5px;
		  padding: 5px;
		}

		.masonry-layout__panel-content {
		  padding: 10px;
		  border-radius: 10px;
		  border: solid 1px gray;
		  background-color: #ddd;
		}

		@media screen and (min-width: 600px) {
			.masonry-layout {
			  column-count: 2;
			 }
		}
		@media screen and (min-width: 800px) {
			.masonry-layout {
			  column-count: 3;
			 }
		}

		@media screen and (min-width: 1000px) {
			.masonry-layout {
			  column-count: 4;
			 }
		}

		@media screen and (min-width: 1200px) {
			.masonry-layout {
			  column-count: 5;
			 }
		}

		#bar {
		 height: 100%;
		 background-color: green;
		}

		#label {

		}

		</style
		</head>

	<body>
	<div class="masonry-layout">

	"""
	return html_header

def html_entry_label(filepath, labels):
	html_entry = """
	<div class="masonry-layout__panel">
    	<div class="masonry-layout__panel-content" align="center">

		<a href="file://{}"><img src="file://{}" width="100%" target="_blank"/></a><br/> {}
		</div>
	</div>
	"""

	# item 0 is the image name
	del labels[0]

	filepath = os.path.normpath( os.path.join(dir_path, filepath) )
	return html_entry.format(filepath, filepath, '<br />'.join(labels) )

def html_entry_scores_table(items):
	
	html = '<div style="max-height:300px; overflow-y:scroll">'
	html += '<table style="width:100%;">'

	for i in range(0, len(items)):
		label = items[i][0]
		score = items[i][1]

		percentString = str( math.ceil( score * 10000.0) / 100.0 ) + '%'

		html += '<tr>'
		html += '<td>'
		html += '<div id="bar" style="height:17px; width:' + percentString + '">'+ label + '</div>'
		html += '</td>'
		html += '<td>' + percentString + '</td>'
		html += '</tr>'

	html += '</table>'
	html += '</div>'

	return html

def html_entry_scores(filepath, scores):
	html_entry = """
	<div class="masonry-layout__panel">
    	<div class="masonry-layout__panel-content" align="center">

		<a href="file://{}"><img src="file://{}" width="100%" target="_blank"/></a><br/> {}
		</div>
	</div>
	"""

	filepath = os.path.normpath( os.path.join(dir_path, filepath) )

	# sort our scores dictionary to highest scoring and to 2 arrays
	# this is a list of tupes of key values.
	items = sorted(scores.items(), key = lambda kv:(kv[1], kv[0]))
	items.reverse()

	return html_entry.format(filepath, filepath, html_entry_scores_table(items ) )

def html_footer():
	html_footer = """
	</div>
	</body>

	</html>
	"""
	return html_footer

# open a file for writing

# for reference, for multi label we want to do :
# gs://calm-trees-123-vcm/flowers/images/5217892384_3edce91761_m.jpg,dandelion,tulip,rose
# from https://cloud.google.com/vision/automl/docs/prepare

start = time.time()

all_files = []
with open(args.output, 'wb') as writer:

	if args.type == 'csv':
 		writer = csv.writer(writer)
 	else:
 		writer.write(html_header())

	# recurse through our image directory and run inference on each image
	for subdir, dirs, files in os.walk(args.imagedir):
		for file in files:
			#print os.path.join(subdir, file)
			filepath = subdir + os.sep + file

			if filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
				all_files.append(filepath)



	all_files.sort()

	#do we shuffle our files?
	if args.random == True:
		random.seed(args.randomseed)
		random.shuffle(all_files)

	#do we limit our file count so we can do a test run?
	if args.limit is not 0:
		all_files = all_files[:args.limit]

	for filepath in all_files:

		pool = NSAutoreleasePool.alloc().init()

		filename = os.path.basename( filepath )
		dirname = os.path.basename ( os.path.dirname( filepath ) )

		# print(dirname)

		image, file = load_image(filepath, resize_to=(Width, Height))
		if image != None:
			labels = []
			scores = {}

			# prepend our prefix if we have it
			if args.prefix:
				labels.append( args.prefix + filepath )
			else:
				labels.append(filepath)

			for model in models:
				prediction = model.predict({'Image': image})



				color_classifier_output = prediction['color_classifier_output']
				location_classifier_output = prediction['location_classifier_output']
				shot_classifier_output = prediction['shot_classifier_output']
				texture_classifier_output = prediction['texture_classifier_output']

				# print(color_classifier_output)


				# combine all dictionaries into one
				color_classifier_output.update(location_classifier_output)
				color_classifier_output.update(shot_classifier_output)
				color_classifier_output.update(texture_classifier_output)
				score = color_classifier_output

				# score = prediction['Scores']

				# print(score)


				# iterate our score dictionary and check our scores against our tolerance.
				# typically we only want 1 label from our model
				# but some of our models are multi label - so if we are above threshold confidence include it.
				# todo: think about this... 
				max_score = 0.0
				max_score_key = None
				for key in score.keys():

					# todo - check if our image path is one of the labels.
					# if it is set the confidence to 1 for that label and set the key to that label
					# this ensures our manually pruned shit sticks with every fold
					if dirname == key.replace('.', '_'):
						print("FORCING LABEL")
						max_score = 1.0
						max_score_key = key


					current_score = score[key]
					if current_score > max_score:
						max_score = current_score
						max_score_key = key

				if max_score_key.endswith('.na'):
					score.pop(max_score_key)

				else: 
					if max_score >= confidence:
						if len(max_score_key) > 32:
							head, sep_, tail = max_score_key.partition('.')
							labels.append(tail.replace('.', '_'))

						else:
							labels.append(max_score_key.replace('.', '_'))

				scores.update(score)

				del prediction

	

			#write all of our predictions out to our CSV
			if args.type == 'csv':
				writer.writerow(labels)
			else:
			# write HTML label version with file name for IMG tag, etc
				
				if args.probabilities:
					writer.write( html_entry_scores(filepath, scores) )
				else:		
					writer.write( html_entry_label(filepath, labels) )

			print("labeled " + filepath)

			# https://github.com/python-pillow/Pillow/issues/2019
			del image
			gc.collect()
	
		file.close()

		pool.release()

	if args.type == 'html':
	 		writer.write(html_footer())

end = time.time()

predictiontime = end - start

print("")
print("Completed Processing")
print("")
print( str( len(all_files) ) + " images processed in " + str(predictiontime) + " seconds")
print( str( len(all_files)/predictiontime ) + "images / second")
print("")



