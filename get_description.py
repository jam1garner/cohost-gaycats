import sys
import os

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# Get path to image to analyze
image_path = sys.argv[1]

# Get authentication variables
subscription_key = os.environ['AZURE_CV_SUBSCRIPTION_KEY']
endpoint = os.environ["AZURE_CV_ENDPOINT"]

# Authenticate
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Open Image
local_image = open(image_path, "rb")

# Describe Image
description_result = computervision_client.describe_image_in_stream(local_image)

# Check if description exists
if not description_result.captions:
    exit(1)
else:
    # Get description with highest confidence
    highest_confidence = 0
    highest_caption = ""
    for caption in description_result.captions:
        if caption.confidence > highest_confidence:
            highest_confidence = caption.confidence
            highest_caption = caption.text

    # print resulting caption
    print(highest_caption)
    exit(0)
