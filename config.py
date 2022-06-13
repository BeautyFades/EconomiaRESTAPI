import os
from google.cloud import secretmanager

environment = 'dev' # Either dev, cloudrun-dev or cloudrun-prd.

if environment == 'dev':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keyfile.json'

# Fetching db_pw secret from Google Cloud Secret Manager
secrets_client = secretmanager.SecretManagerServiceClient()
sec1_name = f"projects/688889779207/secrets/Economy-DB-PW/versions/latest"
sec_1_response = secrets_client.access_secret_version(request={"name": sec1_name})
db_pw = sec_1_response.payload.data.decode("UTF-8")

db_type = 'postgresql'
db_user = 'postgres'
db_host = '34.68.132.15'
db = 'db'