import base64
import dataclasses
import json
from dataclasses import dataclass

import httpx
import jwt
from httpx import Response as HttpxResponse
from httpx import TimeoutException
from requests import Response
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException, Request
from variables import AUTH_0_CLIENT_ID, AUTH_0_JWKS_URL, DEBUG
from json import JSONDecodeError
from typing import Union
from requests.exceptions import Timeout
import logging

_logger = logging.getLogger("backend:app")


@dataclass
class User:
    username: str
    email: str
    sub: str

    def to_json(this):
        return json.dumps(dataclasses.asdict(this))


def fetch_jwks(jwks_url):
    with httpx.Client() as client:
        response = client.get(jwks_url)
        response.raise_for_status()
        return response.json()


def get_public_key(jwks_data, jwt_token) -> str:
    header = jwt.get_unverified_header(jwt_token)
    for key in jwks_data["keys"]:
        if key["kid"] == header["kid"]:
            e_value = int.from_bytes(base64.urlsafe_b64decode(key["e"] + "==="), "big")
            n_value = int.from_bytes(base64.urlsafe_b64decode(key["n"] + "==="), "big")
            return rsa.RSAPublicNumbers(e_value, n_value).public_key(default_backend())
    else:
        raise Exception("Matching public key not found in JWKS.")


def jwt_decode(jwt_token, public_key):
    decoded_token = jwt.decode(jwt_token, public_key, algorithms=["RS256"], audience=AUTH_0_CLIENT_ID)
    return decoded_token


def extract_user(request: Request):
    if DEBUG is True:
        return User(
            username="Krishna",
            email="krishnaveni.rokala@teragonia.com",
            sub="Krishna",
        )

    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if authorization_header.startswith("Bearer "):
        # production mode
        jwt_token = authorization_header.split(" ")[1]
        jwks_url = AUTH_0_JWKS_URL
        jwks_data = fetch_jwks(jwks_url)
        public_key = get_public_key(jwks_data, jwt_token)

        # jwt validation
        res = jwt_decode(jwt_token, public_key)
        return User(username=res["name"], email=res["email"], sub=res["sub"])
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
    

async def async_http_request(
    client, method, url, error="raise", params=None, headers=None, **kwargs
):
    params = params or {}
    headers = headers or {}
    validate_parameters(error)
    try:
        response = await client.request(
            method, url, params=params, headers=headers, **kwargs
        )
    except Exception as e:
        return handle_exception(e, method, url, error)

    return encapsulate_response(response)


def validate_parameters(error: str):
    if error not in ("raise", "ignore"):
        raise ValueError(f"Unknown value {error} for parameter error")
    
def handle_exception(exc: Exception, method: str, url: str, error: str):
    if isinstance(exc, (Timeout, TimeoutException)):
        message = "Timeout on request to url"
    else:
        message = "error sending request to url"

    _logger.error(
        message,
        extra={"method": method, "url": url},
        exc_info=True,
    )

    if error == "raise":
        raise exc

    _logger.info("error ignored", extra={"error": exc})
    return {"response_code": None, "data": {}}


def encapsulate_response(response: Union[Response, HttpxResponse]):
    try:
        data = response.json()
    except (UnicodeDecodeError, JSONDecodeError):
        data = {}

    return {"response_code": response.status_code, "data": data}
