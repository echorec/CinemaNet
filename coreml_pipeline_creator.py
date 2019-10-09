import coremltools
from coremltools.models import datatypes
from coremltools.models.datatypes import Dictionary, Int64, String
import argparse
import os

parser = argparse.ArgumentParser(description='Use a folder of ML model classifiers to label a local unlabeled data set')
parser.add_argument('-m', '--modeldir', type=str, help="folder containing models to be turned into a pipeline", default="./Models/Collab-Multi/2019_10_01_03_27_32", required=False)

args = parser.parse_args()

classifier_filepaths = []
feature_extractor_filepath = ""

for subdir, dirs, files in os.walk(args.modeldir):
	for file in files:
		filepath = subdir + os.sep + file

		if "classifier" in filepath:
			classifier_filepaths.append(filepath)

		if "feature-extractor" in filepath:
			feature_extractor_filepath = filepath


classifier_filepaths.sort()

#feature extractor as input:
feature_extractor_model = coremltools.models.MLModel(feature_extractor_filepath)

# our mobilenet or MNASNet feature exactor has not been fine tuned on purpose (so we can use other models dependent on imagenet features)
feature_exactor_output = "embedding_space"

# update feature input to be named Image
feature_spec = feature_extractor_model.get_spec()
feature_spec.description.input[0].name = "Image"
feature_spec.description.input[0].shortDescription = "Input image"

feature_spec.description.output[0].name = feature_exactor_output
feature_spec.description.output[0].shortDescription = "Mobilenet V2 Embedding Space trained on ImageNet"


print(feature_spec.neuralNetwork.preprocessing)

feature_spec.neuralNetwork.preprocessing[0].featureName = "Image"

for i in range(len(feature_spec.neuralNetwork.layers)):

    # feature exactor input change
    if feature_spec.neuralNetwork.layers[i].input[0] == "mobilenetv2_1.00_224_input__0":
        feature_spec.neuralNetwork.layers[i].input[0] = "Image"

    if feature_spec.neuralNetwork.layers[i].output[0] == "mobilenetv2_1.00_224_input__0":
        feature_spec.neuralNetwork.layers[i].output[0] = "Image"

    # feature exactor output change
    if feature_spec.neuralNetwork.layers[i].input[0] == "global_average_pooling2d__Mean__0":
        feature_spec.neuralNetwork.layers[i].input[0] = feature_exactor_output

    if feature_spec.neuralNetwork.layers[i].output[0] == "global_average_pooling2d__Mean__0":
        feature_spec.neuralNetwork.layers[i].output[0] = feature_exactor_output


# feature_spec.neuralNetworkClassifier.preprocessing[0].featureName = "Image"        

feature_extractor_model = coremltools.models.MLModel(feature_spec)


# color_classifier = coremltools.models.MLModel("/Users/vade/Documents/Repositories/Synopsis/CinemaNet/Models/Collab-Multi/MobileNetV2/Cinemanet-2019-09-26_00_30_42-Color_classifier.mlmodel")
# location_classifier = coremltools.models.MLModel("/Users/vade/Documents/Repositories/Synopsis/CinemaNet/Models/Collab-Multi/MobileNetV2/Cinemanet-2019-09-26_01_16_51-Location_classifier.mlmodel")
# shot_classifier = coremltools.models.MLModel("/Users/vade/Documents/Repositories/Synopsis/CinemaNet/Models/Collab-Multi/MobileNetV2/Cinemanet-2019-09-26_00_59_06-Shot_classifier.mlmodel")
# texture_classifier = coremltools.models.MLModel("/Users/vade/Documents/Repositories/Synopsis/CinemaNet/Models/Collab-Multi/MobileNetV2/Cinemanet-2019-09-26_00_54_19-Texture_classifier.mlmodel")

# # https://forums.developer.apple.com/thread/81571#241998
def convert_multiarray_output_to_image(spec, feature_name, is_bgr=False): 
    """ 
    Convert an output multiarray to be represented as an image 
    This will modify the Model_pb spec passed in. 
    Example: 
        model = coremltools.models.MLModel('MyNeuralNetwork.mlmodel') 
        spec = model.get_spec() 
        convert_multiarray_output_to_image(spec,'imageOutput',is_bgr=False) 
        newModel = coremltools.models.MLModel(spec) 
        newModel.save('MyNeuralNetworkWithImageOutput.mlmodel') 
    Parameters 
    ---------- 
    spec: Model_pb 
        The specification containing the output feature to convert 
    feature_name: str 
        The name of the multiarray output feature you want to convert 
    is_bgr: boolean 
        If multiarray has 3 channels, set to True for RGB pixel order or false for BGR 
    """
    for output in spec.description.input: 
        if output.name != feature_name: 
            continue
        if output.type.WhichOneof('Type') != 'multiArrayType': 
            raise ValueError("%s is not a multiarray type" % output.name) 
        array_shape = tuple(output.type.multiArrayType.shape) 
        channels, height, width = array_shape 
        from coremltools.proto import FeatureTypes_pb2 as ft 
        if channels == 1: 
            output.type.imageType.colorSpace = ft.ImageFeatureType.ColorSpace.Value('GRAYSCALE') 
        elif channels == 3: 
            if is_bgr: 
                output.type.imageType.colorSpace = ft.ImageFeatureType.ColorSpace.Value('BGR') 
            else: 
                output.type.imageType.colorSpace = ft.ImageFeatureType.ColorSpace.Value('RGB') 
        else: 
            raise ValueError("Channel Value %d not supported for image inputs" % channels) 
        output.type.imageType.width = width 
        output.type.imageType.height = height 
 

# # Mark the input layer as image
# feature_extractor_spec = feature_extractor_model.get_spec()

# convert_multiarray_output_to_image(feature_extractor_spec, feature_extractor_spec.description.input[0].name, is_bgr=False)

# feature_extractor_model = coremltools.models.MLModel(feature_extractor_spec)

# input_type = feature_extractor_model.get_spec().description.input[0].type

def uniqueify_model_outputs(model, input_name, output_name):
	spec = model.get_spec()
	
	# Update Output names to be nicer:
	# spec.description.input[0].name = input_name

	spec.description.input[0].name = feature_exactor_output
	spec.description.input[0].shortDescription = "Mobilenet V2 Embedding Space trained on ImageNet"


	#probabilities
	spec.description.output[0].name = output_name
	spec.description.output[0].shortDescription = output_name

	# spec.description.output[1].name = output_name+"_classLabel"
	# spec.description.output[1].shortDescription = output_name+"_classLabel"

	spec.description.predictedProbabilitiesName = output_name
	# spec.description.predictedFeatureName = output_name+"_classLabel"

	for i in range(len(spec.neuralNetworkClassifier.layers)):

		# if spec.neuralNetworkClassifier.layers[i].input[0] == "global_average_pooling2d__Mean__0":
		# 	spec.neuralNetworkClassifier.layers[i].input[0] = input_name

		for j in range(len(spec.neuralNetworkClassifier.layers[i].input)):
		    # feature exactor output change
		    if spec.neuralNetworkClassifier.layers[i].input[j] == "global_average_pooling2d__Mean__0":
		        spec.neuralNetworkClassifier.layers[i].input[j] = feature_exactor_output

			# if spec.neuralNetworkClassifier.layers[i].input[j] == "cinemanet_output__Sigmoid__0":
			# 	print("renaming output to " + output_name)
			# 	spec.neuralNetworkClassifier.layers[i].input[j] = output_name 


		for j in range(len(spec.neuralNetworkClassifier.layers[i].output)):
		    # feature exactor output change
		    # if spec.neuralNetworkClassifier.layers[i].output[j] == "global_average_pooling2d__Mean__0":
		    #     spec.neuralNetworkClassifier.layers[i].output[j] = feature_exactor_output


			if spec.neuralNetworkClassifier.layers[i].output[j] == "cinemanet_output__Sigmoid__0":
				print("renaming output to " + output_name)
				spec.neuralNetworkClassifier.layers[i].output[j] = output_name 

		# elif "final_result__0" in spec.neuralNetworkClassifier.layers[i].output[0]:  
		# 	print("appending output to " + spec.neuralNetworkClassifier.layers[i].output[0].replace("final_result__0", output_name))
		#     spec.neuralNetworkClassifier.layers[i].output[0] = spec.neuralNetworkClassifier.layers[i].output[0].replace("final_result__0", output_name)

	# update our preprocessor input too
	spec.neuralNetworkClassifier.labelProbabilityLayerName = output_name

	# Update our label names
	classLabels = spec.neuralNetworkClassifier.stringClassLabels

	for i in range(len(classLabels.vector)):
		label = classLabels.vector[i]

		
		#clean up labels for production models (not for automl)
		classLabels.vector[i] = classLabels.vector[i].replace("_", ".")

		# we dont prepend our 'TLD' for labels yet.
		# classLabels.vector[i] = 'synopsis.image.' + classLabels.vector[i]


	return coremltools.models.MLModel(spec)


# Load classifiers
classifiers = []

output_features = [ (feature_exactor_output, datatypes.Array(1280)), ]

for classifier_path in classifier_filepaths:

	classifier_name = os.path.basename(classifier_path)
	classifier_name = classifier_name.replace("CinemaNet_", "")
	classifier_name = classifier_name.replace("-classifier.mlmodel", "")

	print classifier_name

	classifier = coremltools.models.MLModel(classifier_path)
	classifier = uniqueify_model_outputs(classifier, classifier_name + "_input", classifier_name + "_output")

	classifiers.append( classifier )

	#build our output features array
	output_features.append( (classifier_name + "_output", datatypes.Dictionary(key_type=String) ) )



# color_classifier = uniqueify_model_outputs(color_classifier, "color_classifier_input", "color_classifier_output")
# location_classifier = uniqueify_model_outputs(location_classifier, "location_classifier_input", "location_classifier_output")
# shot_classifier = uniqueify_model_outputs(shot_classifier, "shot_classifier_input", "shot_classifier_output")
# texture_classifier = uniqueify_model_outputs(texture_classifier, "texture_classifier_input", "texture_classifier_output")


# we will feed out input image to our feature extractor
# we will feed the output of our feature extractor to each classifier 
# we will output all class probabolities into a single probability

input_features = [ ("Image" , datatypes.Array(3,224,224) )] #feature_extractor_spec.description.input[0]

# pipeline = coremltools.models.pipeline.PipelineClassifier(input_features, class_labels, output_features=output_features)

pipeline = coremltools.models.pipeline.Pipeline(input_features, output_features)

pipeline.add_model(feature_extractor_model)

for classifier in classifiers:
	pipeline.add_model(classifier)

# pipeline.add_model(feature_extractor_model)
# pipeline.add_model(color_classifier)
# pipeline.add_model(location_classifier)
# pipeline.add_model(shot_classifier)
# pipeline.add_model(texture_classifier)


# pipeline_spec = coremltools.proto.Model_pb2.Model()

# pipeline_spec.specificationVersion = coremltools._MINIMUM_UPDATABLE_SPEC_VERSION
# pipeline.isUpdatable = False

# Inputs are the inputs from the embedding model
# pipeline_spec.description.input.extend(feature_extractor_spec.description.input[:])

# print(shot_angle_spec.description.output)

# Outputs are the outputs from the classification model
# pipeline_spec.description.output.extend(shot_angle_spec.description.output[:])
# pipeline_spec.description.output.extend(shot_framing_spec.description.output[:])
# pipeline_spec.description.output.extend(shot_subject_spec.description.output[:])
# pipeline_spec.description.output.extend(shot_type_spec.description.output[:])
# pipeline_spec.description.output.extend(places_spec.description.output[:])


# pipeline_spec.description.predictedFeatureName = knn_spec.description.predictedFeatureName,
# pipeline_spec.description.predictedProbabilitiesName = #knn_spec.description.predictedProbabilitiesName,

# Provide metadata,
pipeline.spec.description.metadata.author = 'Anton Marini / Synopsis Project'
pipeline.spec.description.metadata.license = 'BSD'
pipeline.spec.description.metadata.shortDescription = "CinemaNet"

convert_multiarray_output_to_image(pipeline.spec, "Image", is_bgr=False)


# Save the updated spec.,
from coremltools.models import MLModel
mlmodel = coremltools.models.MLModel(pipeline.spec)
output_path = './CinemaNet_Pipeline.mlmodel'

from coremltools.models.utils import save_spec

mlmodel.save(output_path)

