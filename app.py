from flask import Flask, request, Response
import logging, sys
import config
import os
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account
import pandas as pd


if config.environment == 'dev':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keyfile.json'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] | [%(levelname)s] >>> %(message)s', 
                              '%Y-%m-%d %H:%M:%S %Z')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


app = Flask('app')


def get_client_ip_address():
    return request.remote_addr

@app.route("/", methods=["GET"])
def health_check():
    return Response(
            "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': 'alive'}]", 
            status=200, 
            mimetype='application/json'
        )


@app.route("/admin/v1/update_selic/<admin_key>", methods=["POST"])
def copy_latest_selic_data_to_container(admin_key):
    if request.method == 'POST':
        app.logger.info(f'Economia RESTAPI received POST to /admin/v1/update_selic request from {get_client_ip_address()}.')

        if admin_key == 'iamtheboss':
            try:
                app.logger.info(f'Downloading newest data from GCS.')
                gcs_client = storage.Client()
                bucket = gcs_client.get_bucket('economia-webscraper')
                file_name_on_gcs = datetime.today().strftime('%Y_%m_%d_' + 'selic.parquet')
                blob = bucket.blob(f"bcb-selic/{file_name_on_gcs}")

                blob.download_to_filename('latest_selic.parquet')

                app.logger.info(f'Data updated successfully.')
                return Response(
                    "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': 'updated selic rate'}]", 
                    status=200, 
                    mimetype='application/json'
            )

            except Exception as e:
                return Response(
                    "[{'returnStatus': 'fail'}, {'statusCode': '500'}, {'message': "+str(e)+"}]", 
                    status=500, 
                    mimetype='application/json'
            )

        else:
            app.logger.info(f'Economia RESTAPI received FAILED AUTHENTICATION POST to /admin/v1/update_selic {get_client_ip_address()}.')
            return Response(
                    "[{'returnStatus': 'fail'}, {'statusCode': '401'}, {'message': 'unauthorized'}]", 
                    status=401, 
                    mimetype='application/json'
            )

@app.route("/api/v1/latest", methods=["GET"])
def return_latest_data():
    app.logger.info(f'Economia RESTAPI received /api/v1/latest request from {get_client_ip_address()}.')

    try:
        df = pd.read_parquet('latest_selic.parquet')
        json = df.iloc[0].to_json(orient='columns').replace('\\','')
        return Response(
            "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': "+json+"}]", 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        return Response(
            "[{'returnStatus': 'fail'}, {'statusCode': '500'}, {'message': "+str(e)+"}]", 
            status=500, 
            mimetype='application/json'
        )
