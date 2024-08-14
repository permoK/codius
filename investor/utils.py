import uuid
import json
import requests
from requests.auth import HTTPBasicAuth
import base64


def generate_uuid():
    # Generate a UUID4
    full_uuid = uuid.uuid4()

    # Convert the UUID to a string without hyphens
    # short_uuid = str(full_uuid).replace("-", "")
    short_uuid = (full_uuid)

    # Use only the first 12 characters
    code = short_uuid

    return code

########## global variable #######
base_url = 'https://monadoll.tech/'
key = 'nAbuuqCD0dMH3uhXSO5A2yY7rd1HACYE'
secret = '3ZnvWnVqFqPgvUXF'
####################################

######################### ACCESS TOKEN ##################################
def get_access_token():
    consumer_key = key
    consumer_secret = secret
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    # data = json.loads(r.text)
# Check if the request was successful
    if r.status_code == 200:
        # Parse JSON content
        data = json.loads(r.text)
        # Access the token
        access_token = data.get("access_token")
        return access_token
    else:
        # Handle error response
        return None
########################## END ACCESS TOKEN #############################

