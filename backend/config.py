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

    # AWS credentials
    aws_account_id = environ.get('AWS_ACCOUNT_ID')
    aws_access_key = environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = environ.get('AWS_SECRET_ACCESS_KEY')
    aws_user = environ.get('AWS_USER')
    aws_region = environ.get('AWS_REGION')

    # App-related
    bound_port = 5000
    domain_url = environ.get('DOMAIN_URL')
    whitelisted_origins = environ.get('WHITELISTED_ORIGINS')
    SECRET_KEY = environ.get('SECRET_KEY') or '0y4TJIyEjH8ZVkXPMGBiFEcHk8tdfe57kE1IJhvR1yb1cmWY'

    if SECRET_KEY != environ.get('SECRET_KEY'):
        logger.warning("Error loading SECRET_KEY!  Temporarily using a hard-coded key.")

    logger.debug("End of the Config() class.")