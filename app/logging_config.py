"""Logging configuration.

One stdlib dictConfig covers everything: our own loggers plus the libraries
already logging through stdlib (uvicorn, strawberry.execution, httpx2).
"""

import logging.config

from app.settings import settings


def configure_logging() -> None:
    level = settings.log_level.upper()
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            # uvicorn loggers don't propagate to root: point them at our
            # handler so every line shares the same format
            "loggers": {
                # httpcore2 floods DEBUG with connection internals
                "httpcore2": {"level": "INFO"},
                # httpx2 logs every request at INFO, duplicating our own
                # upstream log line (which also carries the duration)
                "httpx2": {"level": "WARNING"},
                "uvicorn": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )
