import os 
import argparse
import coremltools
from coremltools.models import datatypes

parser = argparse.ArgumentParser(description='List all labels from our models')
parser.add_argument('-m', '--modeldir', type=str, help='folder containing core ml models to clean', default='./Models/Classifiers/Cleaned/', required=False)


args = parser.parse_args()

# load our models into our models array
dir_path = os.getcwd()

models_path = os.path.normpath( os.path.join(dir_path, args.modeldir) )

print('Loading Models from: ' + models_path)


def printLabels(originalModelFileName):
	model = coremltools.models.MLModel(models_path + '/' + originalModelFileName)
	spec = model.get_spec()

	# Update our label names
	classLabels = spec.neuralNetworkClassifier.stringClassLabels

	for i in range(len(classLabels.vector)):
		label = classLabels.vector[i]

		if label.endswith('.na'):
			continue;
		else:
			print(label)


model_paths = []

for filename in os.listdir(models_path):
	if filename.endswith('.mlmodel'):	
		model_path = filename

		if model_path:
			model_paths.append(model_path)
	else:
		continue


model_paths.sort()


for model_path in model_paths:
	printLabels(model_path)
