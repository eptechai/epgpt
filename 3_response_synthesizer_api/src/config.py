import logging
import os
from pathlib import Path

path = Path(__file__).parent.parent.joinpath("data").as_posix()

LOGGER = logging.getLogger()

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*")



