import os
import importlib
import pytest


@pytest.fixture(scope="function")
def set_env(request):
    """
    Since the settings module is loaded once, we need to make sure we can test different environments.
    We use a fixture to parametrize tests.
    """
    original_env = os.environ.get('ENV_TYPE')
    os.environ['ENV_TYPE'] = request.param
    from mcp_llamaindex import config
    importlib.reload(config)
    yield config.settings
    if original_env is not None:
        os.environ['ENV_TYPE'] = original_env
    else:
        del os.environ['ENV_TYPE']
    # Reload config to reset to original state
    importlib.reload(config)

@pytest.mark.parametrize("env_type", ["dev"])
def test_env_file_exists(env_type):
    """Test that the .env file exists for the given environment."""
    from mcp_llamaindex import config

    expected_env_file_name = f".{env_type}.env"
    env_file = config.settings.PACKAGE_ROOT.parent.parent / expected_env_file_name
    assert env_file.exists(), f"No env file found at {env_file} for {env_type} environment. Please create one."


@pytest.mark.parametrize("set_env, expected", [
    ("dev", {"ENV_TYPE": "dev", "LOG_LEVEL": "INFO"}),
], indirect=["set_env"])
def test_dev_settings(set_env, expected):
    """
    Test that the correct settings are loaded for the dev environment.
    """
    settings = set_env
    assert settings.ENV_TYPE == expected["ENV_TYPE"]
    assert settings.LOG_LEVEL == expected["LOG_LEVEL"]
    assert str(settings.SERVER_LOG_FILE).endswith("dev_server.log")

@pytest.mark.skip(reason="No testing for prod env for now")
@pytest.mark.parametrize("set_env, expected", [
    ("prod", {"ENV_TYPE": "prod", "LOG_LEVEL": "INFO"}),
], indirect=["set_env"])
def test_prod_settings(set_env, expected):
    """
    Test that the correct settings are loaded for the prod environment.
    """
    settings = set_env
    assert settings.ENV_TYPE == expected["ENV_TYPE"]
    assert settings.LOG_LEVEL == expected["LOG_LEVEL"]
    assert settings.DATABASE_URL == expected["DATABASE_URL"]
    assert str(settings.SERVER_LOG_FILE).endswith("prod_server.log")
