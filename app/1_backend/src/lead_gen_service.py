import pickle
from typing import List

from fastapi import HTTPException
from httpx import AsyncClient, AsyncHTTPTransport
from urllib.parse import urljoin

import logging

from utils import async_http_request, encapsulate_response
from variables import RESPONSE_SYNTHESIZER_API_HOST

class ResponseSynthesizerService:
    """
    ResponseSynthesizerService is a class that handles the API calls to the server which hosts the conversational indices.
    """

    def __init__(self, id: str) -> None:
        self.id = id
        self.url = RESPONSE_SYNTHESIZER_API_HOST


    async def get_structured_job_posting(
        self,
        copied_posting: str
    ):
        """
        Sends a prompt to the model server and returns the response
        :param prompt: Prompt string
        :return: Response string
        """
        request_url = urljoin(self.url, f"/response/posting/{self.id}")
        request_params = {
            "copied_posting": copied_posting
        }
        _logger.info(f"Request Synthesyze to {request_url}")
        async with AsyncClient(
            timeout=20, transport=AsyncHTTPTransport(retries=3)
        ) as client:
            response = (
                await async_http_request(
                    client, "GET", request_url, "ignore", params=request_params
                )
            )
        print(response)
        _logger.info(f"Response Synthesyze to {response}")
        return response


    async def get_proposal(self):
        """
        Returns the current model parameters
        :return: Model parameters
        """
        request_url = urljoin(self.url, f"/v1/params/")
 
        async with AsyncClient(
            timeout=2, transport=AsyncHTTPTransport(retries=3)
        ) as client:
            response = (
                await async_http_request(
                    client, "GET", request_url, "ignore", params=None
                )
            )["data"]

        return {k: value for k, value in response.items()}
