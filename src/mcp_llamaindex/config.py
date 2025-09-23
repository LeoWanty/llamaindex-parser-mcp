from pathlib import Path

# Env type
ENV_TYPE = "dev"

# Paths
PACKAGE_ROOT = Path(__file__).parent
STATIC_DIR = PACKAGE_ROOT / "STATIC"

# logs
SERVER_LOG_FILE = STATIC_DIR / f"{ENV_TYPE}_server.log"