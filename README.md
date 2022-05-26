# GCP Cloud Run Economia REST API

## To deploy locally with Docker
When deployed to GCRun, the environment variable _GOOGLE_APPLICATION_CREDENTIALS_ is set automatically, so locally you must uncomment lines 11 and 12 in **SelicExtractor.py** and have a valid GCP credentials file with enough permissions inside the Docker container for it to be referenced.
1. Make sure that the environment variable _GOOGLE_APPLICATION_CREDENTIALS_ is going to be set corrently by placing the key ```.json``` file together with the other files (Dockerfile, app.py, SelicExtractor.py, etc.). It is going to be copied to the container and be referenced in the code to access GCS, BQ and other resources.
2. ```cd``` to the directory containg all files and run ```docker build -t restapi .```
3. Execute ```docker run -p 8001:8081 restapi```
4. Access the Flask routes by going to ```http://127.0.0.1:8001/<route_name>```

## Deploy to Google Cloud Run
To deploy to the cloud, there's no need to set credentials since the environment variable is set automatically (see [here!](https://cloud.google.com/run/docs/configuring/service-accounts#:~:text=By%20default%2C%20Cloud%20Run%20services,most%20minimal%20set%20of%20permissions.)).
1. Pull this repository and ```cd``` into the folder
2. Make sure you're logged into your GCloud project and run ```gcloud builds submit --tag gcr.io/<PROJECT_ID>/<IMAGE_NAME> .```. This will build the container using Cloud Build.
3. Deploy to Cloud Run using ```gcloud beta run deploy <GCR_INSTANCE_NAME> --image gcr.io/<PROJECT_ID>/<IMAGE_NAME> --region southamerica-east1 --platform managed --allow-unauthenticated --quiet```. Be aware of the _allow-unauthenticated_ flag: anyone can access the endpoint so it's best to secure it as a next step.
