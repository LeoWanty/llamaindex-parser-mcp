import logging
import sys

from mcp_llamaindex.config import settings

# Set some new handlers and formatters for FastMCP server
# As FastMCP implements a middleware logger, we modify it here to fit the project needs

log_level = logging.getLevelName(settings.LOG_LEVEL)

# --- Correct Logging Configuration ---
root_logger = logging.getLogger()

formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s\t%(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
)

# Console handler
console_handler = logging.StreamHandler(stream=sys.stderr)
console_handler.setLevel(logging.INFO)  # What appears in the client notifications
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(
    filename=settings.SERVER_LOG_FILE, mode="a", encoding="utf-8"
)
file_handler.setLevel(log_level)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Set the overall root logger level to DEBUG
root_logger.setLevel(log_level)
