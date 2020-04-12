"""Defines an object used to configure parameters for our Flask app."""
from backend.global_logger import logger, local
from os import environ


class Config(object):
    logger.debug("Start of the Config() class.")

    # Apply the environment variables when running locally
    # When running in GCP, these are loaded from the env_variables.yaml file when the app loads
    if local:
        from env_tools import apply_env
        apply_env()
        logger.info("Local .env variables applied.")
        DEBUG = True
    else:
        DEBUG = False

    # Load AWS credentials
    AWS_ACCOUNT_ID = environ.get('AWS_ACCOUNT_ID')
    AWS_ACCESS_KEY = environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_USER = environ.get('AWS_USER')
    AWS_REGION = environ.get('AWS_REGION')

    # Load app-related credentials
    BOUND_PORT = 5000
    # DOMAIN_URL = environ.get('DOMAIN_URL')
    WHITELISTED_ORIGINS = environ.get('WHITELISTED_ORIGINS')
    SECRET_KEY = environ.get('SECRET_KEY') or '0y4TJIyEjH8ZVkXPMGBiFEcHk8tdfe57kE1IJhvR1yb1cmWY'

    if SECRET_KEY != environ.get('SECRET_KEY'):
        logger.warning("Error loading SECRET_KEY!  Temporarily using a hard-coded key.")

    logger.debug("End of the Config() class.")
