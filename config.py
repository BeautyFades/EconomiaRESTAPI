import os
from google.cloud import secretmanager

ENVIRONMENT = 'dev' # Either dev, cloudrun-dev or cloudrun-prd.

if ENVIRONMENT == 'dev':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keyfile.json'

SOURCE_BUCKET_NAME = 'economia-webscraper'
SOURCE_PATH = 'bcb-selic'

# Fetching db_pw secret from Google Cloud Secret Manager
secrets_client = secretmanager.SecretManagerServiceClient()
sec1_name = f"projects/688889779207/secrets/Economy-DB-PW/versions/latest"
sec_1_response = secrets_client.access_secret_version(request={"name": sec1_name})
DB_PW = sec_1_response.payload.data.decode("UTF-8")

DB_TYPE = 'postgresql'
DB_USER = 'postgres'
DB_HOST = '34.68.132.15'
DB_NAME = 'db'