import config
import sys
from google.cloud import logging


class RESTAPILogger():
    def __init__(self):
        if config.ENVIRONMENT != 'dev':
            client = logging.Client()
            client.setup_logging()

    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] | [%(levelname)s] >>> %(message)s', 
                              '%Y-%m-%d %H:%M:%S %Z')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)