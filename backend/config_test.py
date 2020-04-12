"""Unit tests for the Config class to ensure environment variables are loaded."""
from backend.config import Config
from env_tools import apply_env


def test_config():
    # Apply environment variables
    apply_env()

    # AWS credentials
    assert Config.AWS_ACCOUNT_ID is not None
    assert Config.AWS_ACCESS_KEY is not None
    assert Config.AWS_SECRET_ACCESS_KEY is not None
    assert Config.AWS_USER is not None
    assert Config.AWS_REGION is not None

    # App-related
    assert Config.BOUND_PORT is not None
    # assert Config.DOMAIN_URL is not None
    assert Config.WHITELISTED_ORIGINS is not None
    assert Config.SECRET_KEY is not None
    assert Config.DEBUG is not None
