import os

DEBUG = os.environ.get("DEBUG", "False") == "True"
bind = "0.0.0.0:8000"
timeout = 180

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False if DEBUG else True,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(asctime)s] [%(levelname)s] [%(name)s] (%(filename)s:%(funcName)s@%(lineno)s): %(message)s",
            "use_colors": None,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "WARNING",  # Change the log level here to WARNING
    },
}
