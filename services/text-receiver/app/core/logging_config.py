"""
Logging configuration.

Sets a consistent logging format and exports a logger instance used across the project.
"""


import logging

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Export logger instance for other modules
logger = logging.getLogger(__name__)
