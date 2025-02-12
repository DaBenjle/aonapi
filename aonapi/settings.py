import logging
import logging.config
from pathlib import Path

# Define the defaults directly in the settings file
database_url = "sqlite:///db.sqlite3"
debug = False

# URLs - Define them directly in the settings file
aon_protocol = "https"
aon_base_url = "aonprd.com"
elastic_search_prefix = "elasticsearch"
search_url = f"{aon_protocol}://{elastic_search_prefix}.{aon_base_url}/json-data"
index_path = f"{search_url}/aon52-index.json"


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if debug else "INFO",
    },
    "loggers": {
        "uvicorn": {
            "level": "DEBUG" if debug else "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "DEBUG" if debug else "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "DEBUG" if debug else "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "level": "DEBUG" if debug else "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
