 # TODO(developer): Uncomment and set the following variables
project_id = 'dev-sphere-240918'
compute_region = 'us-central1'
model_id = 'ICN3999305010485765968'
filter_ = 'filter expression here'

from google.cloud import automl_v1beta1 as automl

client = automl.AutoMlClient()

# Get the full path of the model.
model_full_id = client.model_path(project_id, compute_region, model_id)

# List all the model evaluations in the model by applying filter.
response = client.list_model_evaluations(model_full_id, filter_)

print("List of model evaluations:")
for element in response:
    print(element)