import coremltools
from coremltools.models import datatypes
from coremltools.models.datatypes import Dictionary, Int64, String

#feature extractor as input:
feature_extractor_model = coremltools.models.MLModel("Models/Collab-Multi/Cinemanet-2019-09-24_16_48_36-Color_feature.mlmodel")

# update feature input to be named Image
feature_spec = feature_extractor_model.get_spec()
feature_spec.description.input[0].name = "Image"
feature_spec.description.input[0].shortDescription = "Input image"

print(feature_spec.neuralNetwork.preprocessing)

feature_spec.neuralNetwork.preprocessing[0].featureName = "Image"

for i in range(len(feature_spec.neuralNetwork.layers)):

    if feature_spec.neuralNetwork.layers[i].input[0] == "NASNet_input__0":
        feature_spec.neuralNetwork.layers[i].input[0] = "Image"

    if feature_spec.neuralNetwork.layers[i].output[0] == "NASNet_input__0":
        feature_spec.neuralNetwork.layers[i].output[0] = "Image"

# feature_spec.neuralNetworkClassifier.preprocessing[0].featureName = "Image"        

feature_extractor_model = coremltools.models.MLModel(feature_spec)


# classifier outputs:

color_classifier = coremltools.models.MLModel("Models/Collab-Multi/Cinemanet-2019-09-24_16_48_36-Color_classifier.mlmodel")
location_classifier = coremltools.models.MLModel("Models/Collab-Multi/Cinemanet-2019-09-24_17_12_52-Location_classifier.mlmodel")
shot_classifier = coremltools.models.MLModel("Models/Collab-Multi/Cinemanet-2019-09-24_16_54_12-Shot_classifier.mlmodel")
texture_classifier = coremltools.models.MLModel("Models/Collab-Multi/Cinemanet-2019-09-24_16_49_19-Texture_classifier.mlmodel")

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

		for j in range(len(spec.neuralNetworkClassifier.layers[i].output)):
			# if spec.neuralNetworkClassifier.layers[i].output[j] ==  "classLabel":
				# print("renaming classLabel")
				# spec.neuralNetworkClassifier.layers[i].output[j] = output_name + "_classLabel"

			if spec.neuralNetworkClassifier.layers[i].output[j] == "cinemanet_output__Sigmoid__0":
				print("renaming output to " + output_name)
				spec.neuralNetworkClassifier.layers[i].output[j] = output_name 

		# elif "final_result__0" in spec.neuralNetworkClassifier.layers[i].output[0]:  
		# 	print("appending output to " + spec.neuralNetworkClassifier.layers[i].output[0].replace("final_result__0", output_name))
		#     spec.neuralNetworkClassifier.layers[i].output[0] = spec.neuralNetworkClassifier.layers[i].output[0].replace("final_result__0", output_name)

	# update our preprocessor input too
	spec.neuralNetworkClassifier.labelProbabilityLayerName = output_name

	return coremltools.models.MLModel(spec)


color_classifier = uniqueify_model_outputs(color_classifier, "color_classifier_input", "color_classifier_output")
location_classifier = uniqueify_model_outputs(location_classifier, "location_classifier_input", "location_classifier_output")
shot_classifier = uniqueify_model_outputs(shot_classifier, "shot_classifier_input", "shot_classifier_output")
texture_classifier = uniqueify_model_outputs(texture_classifier, "texture_classifier_input", "texture_classifier_output")


# we will feed out input image to our feature extractor
# we will feed the output of our feature extractor to each classifier 
# we will output all class probabolities into a single probability

input_features = [ ("Image" , datatypes.Array(3,224,224) )] #feature_extractor_spec.description.input[0]

output_features=[ (	"color_classifier_output", datatypes.Dictionary(key_type=String) ),
					("location_classifier_output", datatypes.Dictionary(key_type=String) ),
					("shot_classifier_output",datatypes.Dictionary(key_type=String) ),
					("texture_classifier_output", datatypes.Dictionary(key_type=String) ),
				]

class_labels = [
	#shot angle
	"high", "tilted", "aerial", "low",

	#shot framing
	"low","medium","close up","extreme close up","long","extreme long",
		
	#shot subject
	"people", "text", "face", "person", "animal", "faces"

	#shot type
	"over the shoulder","portrait","two shot","master",

	#places
	"office building", "veterinarians office", "viaduct", "nursery", "mansion", "television studio", "mountain path", "throne room", "stable", "restaurant kitchen", "wave", "gift shop", "waiting room", "apartment building outdoor", "harbor", "topiary garden", "trench", "building facade", "tree farm", "underwater ocean deep", "attic", "heliport", "field wild", "hardware store", "storage room", "street", "physics laboratory", "kennel outdoor", "shopping mall indoor", "swimming pool indoor", "escalator indoor", "bank vault", "airport terminal", "elevator shaft", "biology laboratory", "golf course", "ice skating rink outdoor", "ski slope", "coffee shop", "balcony interior", "art school", "supermarket", "hangar outdoor", "home theater", "gazebo exterior", "forest road", "garage indoor", "museum outdoor", "garage outdoor", "islet", "sky", "bazaar outdoor", "stadium soccer", "hospital", "vineyard", "manufactured home", "amusement park", "raft", "library indoor", "porch", "alcove", "tundra", "forest path", "downtown", "berth", "bow window indoor", "jail cell", "locker room", "stadium football", "general store indoor", "sushi bar", "crevasse", "campsite", "pond", "baseball field", "butchers shop", "beach", "mountain snowy", "staircase", "farm", "swimming hole", "wind farm", "arch", "repair shop", "classroom", "badlands", "orchard", "mezzanine", "corral", "sandbox", "auto factory", "lagoon", "wheat field", "patio", "office", "general store outdoor", "church outdoor", "shopfront", "elevator door", "schoolhouse", "water park", "racecourse", "courthouse", "marsh", "beach house", "dam", "hot spring", "entrance hall", "greenhouse outdoor", "volcano", "doorway outdoor", "subway station platform", "basketball court indoor", "house", "fishpond", "pantry", "elevator lobby", "dining hall", "toyshop", "ballroom", "motel", "lock chamber", "field road", "fountain", "playground", "football field", "pizzeria", "hunting lodge outdoor", "highway", "beer garden", "bullring", "parking lot", "cockpit", "catacomb", "river", "yard", "hospital room", "martial arts gym", "rainforest", "castle", "office cubicles", "church indoor", "bus interior", "discotheque", "art gallery", "galley", "loading dock", "cabin outdoor", "assembly line", "drugstore", "arena rodeo", "hayfield", "residential neighborhood", "park", "junkyard", "oilrig", "iceberg", "desert vegetation", "beauty salon", "shower", "snowfield", "kasbah", "railroad track", "computer room", "nursing home", "conference center", "palace", "grotto", "alley", "mountain", "synagogue outdoor", "ticket booth", "fire station", "food court", "artists loft", "library outdoor", "promenade", "shoe shop", "lawn", "swamp", "arena hockey", "art studio", "bus station indoor", "bedroom", "fastfood restaurant", "phone booth", "ruin", "hotel room", "rope bridge", "bakery shop", "natural history museum", "water tower", "bridge", "restaurant patio", "banquet hall", "coast", "boathouse", "basement", "bar", "embassy", "corn field", "raceway", "industrial area", "excavation", "inn outdoor", "operating room", "botanical garden", "driveway", "barn", "construction site", "closet", "aqueduct", "fire escape", "lake natural", "skyscraper", "crosswalk", "living room", "clothing store", "chemistry lab", "courtyard", "aquarium", "butte", "legislative chamber", "kitchen", "ski resort", "pagoda", "restaurant", "army base", "archaelogical excavation", "bazaar indoor", "candy store", "barndoor", "diner outdoor", "canyon", "jewelry shop", "village", "temple asia", "wet bar", "landing deck", "lighthouse", "recreation room", "car interior", "chalet", "athletic field outdoor", "forest broadleaf", "ice cream parlor", "boxing ring", "runway", "moat water", "orchestra pit", "delicatessen", "ball pit", "parking garage indoor", "dorm room", "canal urban", "bedchamber", "campus", "booth indoor", "corridor", "boat deck", "windmill", "department store", "sauna", "waterfall", "lobby", "arena performance", "japanese garden", "ocean", "volleyball court outdoor", "vegetable garden", "parking garage outdoor", "mausoleum", "zen garden", "ice shelf", "roof garden", "server room", "conference room", "television room", "cemetery", "pharmacy", "airfield", "field cultivated", "mosque outdoor", "home office", "rock arch", "utility room", "market indoor", "pier", "ice floe", "oast house", "train interior", "flea market indoor", "clean room", "movie theater indoor", "amusement arcade", "tower", "auditorium", "shed", "creek", "dining room", "youth hostel", "burial chamber", "pasture", "tree house", "balcony exterior", "train station platform", "ice skating rink indoor", "stage outdoor", "bathroom", "slum", "desert road", "soccer field", "playroom", "florist shop indoor", "bamboo forest", "plaza", "pub indoor", "childs room", "swimming pool outdoor", "watering hole", "pet shop", "cafeteria", "arcade", "dressing room", "airplane cabin", "atrium public", "bowling alley", "valley", "museum indoor", "auto showroom", "stadium baseball", "canal natural", "greenhouse indoor", "bookstore", "cottage", "lecture room", "science museum", "formal garden", "market outdoor", "kindergarden classroom", "pavilion", "hotel outdoor", "desert sand", "rice paddy", "gymnasium indoor", "amphitheater", "boardwalk", "engine room", "hangar indoor", "archive", "beer hall", "glacier", "stage indoor", "music studio", "gas station", "carrousel", "medina", "cliff", "fabric store", "picnic area", "jacuzzi indoor", "landfill", "reception", "laundromat", "igloo",
]


# pipeline = coremltools.models.pipeline.PipelineClassifier(input_features, class_labels, output_features=output_features)

pipeline = coremltools.models.pipeline.Pipeline(input_features, output_features)

pipeline.add_model(feature_extractor_model)
pipeline.add_model(color_classifier)
pipeline.add_model(location_classifier)
pipeline.add_model(shot_classifier)
pipeline.add_model(texture_classifier)


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

