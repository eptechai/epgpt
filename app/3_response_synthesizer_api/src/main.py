

from fastapi import FastAPI # pylint: disable=C0413

from api import init_api

#
#   This file is kept separate to explicitly allow uvicorn to startup FastAPI.
#
app: FastAPI = init_api()
