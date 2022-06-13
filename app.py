from flask import Flask, request, Response, send_file
import logging, sys
import config
import os
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account
from ScraperLogger import ScraperLogger
from DBConnector import DBConnector
import pandas as pd


if config.environment == 'dev':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keyfile.json'

l = ScraperLogger()

app = Flask('app')


def get_client_ip_address():
    return request.remote_addr

@app.route("/", methods=["GET"])
def health_check():

    logging.info(f'Economia RESTAPI received / request from {get_client_ip_address()}. Health checking...')
    return Response(
            "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': 'alive'}]", 
            status=200, 
            mimetype='application/json'
        )


@app.route("/admin/v1/update_db/<admin_key>", methods=["POST"])
def update_db_with_latest_gcs_data(admin_key):
    if request.method == 'POST':
        logging.info(f'Economia RESTAPI received POST to /admin/v1/update_db request from {get_client_ip_address()}.')

        if admin_key == 'iamtheboss':
            try:
                logging.info(f'Downloading newest data from GCS to container.')
                gcs_client = storage.Client()
                bucket = gcs_client.get_bucket('economia-webscraper')
                file_name_on_gcs = datetime.today().strftime('%Y_%m_%d_' + 'selic.parquet')
                blob = bucket.blob(f"bcb-selic/{file_name_on_gcs}")

                blob.download_to_filename('latest_selic.parquet')
                logging.info(f'Data downloaded successfully. Starting insertion')

                df = pd.read_parquet('latest_selic.parquet')
                elems = df.values.tolist()
                query_values = ''

                # Formatting the query_values variable so it can be passed as a SQL parameter to a INSERT INTO statement
                for i in range(len(elems)):
                    row = f"({elems[i][0]}, '{elems[i][1]}', '{elems[i][2]}', '{elems[i][3]}', '{elems[i][4]}', '{elems[i][5]}', '{elems[i][6]}')"
                    row = row.replace("'None'", 'null') # In case there are None values, replace them with Postgres null, without quotes.

                    query_values = query_values + str(row) + ', '

                query_values = query_values[:-2] # Removing last two characters (', ') at the very end of string.
                
                db = DBConnector(config.db_type, config.db_user, config.db_pw, config.db_host, config.db)
                db.execute_query(f"INSERT INTO selic VALUES {query_values} ON CONFLICT (n_reuniao) DO NOTHING")

                return Response(
                    "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': 'updated selic rate on database'}]", 
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
            logging.info(f'Economia RESTAPI received FAILED AUTHENTICATION POST to /admin/v1/update_db {get_client_ip_address()}.')
            return Response(
                    "[{'returnStatus': 'fail'}, {'statusCode': '401'}, {'message': 'unauthorized'}]", 
                    status=401, 
                    mimetype='application/json'
            )

@app.route("/api/v1/latest/<n>", methods=["GET"])
def return_latest_data(n):
    logging.info(f'Economia RESTAPI received /api/v1/latest request from {get_client_ip_address()}.')

    # Define dumping auxiliary functions
    def dump_datetime(value):
        """Deserialize DATETIME object into string form for JSON processing."""
        if value is None:
            return 'null'
        return value.strftime("%d/%m/%Y")

    def dump_numeric(value):
        """Deserialize NUMERIC object into string form for JSON processing."""
        if value is None:
            return 'null'
        return float(value)

    try:
        db = DBConnector(config.db_type, config.db_user, config.db_pw, config.db_host, config.db)
        r = db.execute_query(f"SELECT n_reuniao, data_reuniao, data_inicio_vigencia, data_fim_vigencia, meta_selic_aa, taxa_selic_aa, taxa_selic_am FROM selic ORDER BY n_reuniao DESC LIMIT {n}").fetchall()
        logging.info(r)
        index = 0
        results_dict = {}
        for entry in r:
            results_dict[index] = {'n_reuniao': r[index][0],
                'data_reuniao': dump_datetime(r[index][1]),
                'data_inicio_vigencia': dump_datetime(r[index][2]),
                'data_fim_vigencia': dump_datetime(r[index][3]),
                'meta_selic_aa': dump_numeric(r[index][4]),
                'taxa_selic_aa': dump_numeric(r[index][5]),
                'taxa_selic_am': dump_numeric(r[index][6]),
                }
            index += 1

        return Response(
            "[{'returnStatus': 'success'}, {'statusCode': '200'}, {'message': "+str(results_dict)+"}]", 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        return Response(
            "[{'returnStatus': 'fail'}, {'statusCode': '500'}, {'message': "+str(e)+"}]", 
            status=500, 
            mimetype='application/json'
        )
