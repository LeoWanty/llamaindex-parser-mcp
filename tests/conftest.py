import os
import pytest
from pathlib import Path

TEST_DIR = Path(__file__).parent
STATIC_DIR = TEST_DIR / "static"
GENERATED_EXAMPLES_DIR = STATIC_DIR / "generated_examples"

@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    """
    Sets the environment type to 'dev' for the entire test session.
    This ensures that the correct .env file is loaded for the tests.
    """
    os.environ["ENV_TYPE"] = "dev"