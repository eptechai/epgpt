from google.cloud import logging

from . import variables as vars


def configure_gcp_logging():
    if not vars.DEBUG:
        client = logging.Client.from_service_account_info(vars.CREDENTIALS)
        client.setup_logging()

        print("Configured GCP logging...")
