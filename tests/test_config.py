import os
import importlib
import pytest

# Since the settings module is loaded once, we need to make sure
# we can test both environments. We use a fixture to parametrize tests.
@pytest.fixture(scope="function")
def set_env(request):
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

@pytest.mark.parametrize("set_env, expected", [
    ("dev", {"ENV_TYPE": "dev", "LOG_LEVEL": "DEBUG", "DATABASE_URL": "sqlite:///./test.db"}),
], indirect=["set_env"])
def test_dev_settings(set_env, expected):
    """
    Test that the correct settings are loaded for the dev environment.
    """
    settings = set_env
    assert settings.ENV_TYPE == expected["ENV_TYPE"]
    assert settings.LOG_LEVEL == expected["LOG_LEVEL"]
    assert settings.DATABASE_URL == expected["DATABASE_URL"]
    assert str(settings.SERVER_LOG_FILE).endswith("dev_server.log")

@pytest.mark.parametrize("set_env, expected", [
    ("prod", {"ENV_TYPE": "prod", "LOG_LEVEL": "INFO", "DATABASE_URL": "postgresql://user:password@prod-db:5432/mydatabase"}),
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
