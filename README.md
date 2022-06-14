# GCP Cloud Run Economia REST API

## Required Infrastructure
This project requires the usage of this repository and [this one](https://github.com/BeautyFades/WebScraper) for deployment. This repository is a REST API and the other one is for the webscraper. Besides these, you will also need a DB. I've hosted mine on CloudSQL with Postgres and added the default user's password as a Secret on Cloud Secret Manager. For this repository, the changes that need to be applied are inside the _config.py_ file. Keep in mind the DB IP Address, Username, Type, and Password (I recommend using a Secret Manager instead of hardcoding the password). The Database should have a table called ```selic``` with the following schema to work without further edits:

![Schema](https://i.imgur.com/9AyvlIs.png)

## To deploy locally with Docker
When deployed to GCRun, the environment variable _GOOGLE_APPLICATION_CREDENTIALS_ is set automatically, so in order to deploy locally you must have a valid GCP credentials file with enough permissions inside the Docker container for it to be referenced. You must also confirm that in the _config.py_ you have the environment set to ```dev```. The step by step guide is as follows:
1. Make sure that the environment variable _GOOGLE_APPLICATION_CREDENTIALS_ is going to be set corrently by placing the GCP Service Account credentials file ```keyfile.json``` together with the other files in the root folder (along with the Dockerfile, app.py, etc.). It is going to be copied to the container and be referenced in the code to access GCS, BigQuery, Secret Manager. You must also make sure it has enough permissions for the resources it is going to access.
2. ```cd``` to the directory containg all files and run ```docker build -t <IMAGE_NAME> .```, such as ```docker build -t restapi .```
3. Execute ```docker run -p 8001:8081 <IMAGE_NAME>```, such as ```docker run -p 8001:8081 restapi```
4. Access the Flask routes by going to ```http://127.0.0.1:8001/<route_name>```

## Deploy to Google Cloud Run
To deploy to the cloud, there's no need to set credentials since the environment variable is set automatically (see [here!](https://cloud.google.com/run/docs/configuring/service-accounts#:~:text=By%20default%2C%20Cloud%20Run%20services,most%20minimal%20set%20of%20permissions.)).
1. Pull this repository and ```cd``` into the folder
2. Make sure you're logged into your GCloud project and run ```gcloud builds submit --tag gcr.io/<PROJECT_ID>/<IMAGE_NAME> .```. This will build the container using Cloud Build.
3. Deploy to Cloud Run using ```gcloud beta run deploy <GCR_INSTANCE_NAME> --image gcr.io/<PROJECT_ID>/<IMAGE_NAME> --region southamerica-east1 --platform managed --allow-unauthenticated --quiet```. Be aware of the _allow-unauthenticated_ flag: anyone can access the endpoint so it's best to secure it as a next step.
