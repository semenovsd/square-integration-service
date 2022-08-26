import asyncio
from asyncio import Protocol
from typing import Tuple, TypeVar, final

from aiohttp import ClientError, ClientResponse, ClientSession
from loguru import logger

from services.utils.decorators import async_retry

ResponseType = TypeVar('ResponseType', dict, None)


class AsyncHTTPClientBase(Protocol):
    """Base class http/https interface for case many request to one server."""

    _session: ClientSession = None
    _correct_response_statuses: Tuple[int] = (200, 201)

    @classmethod
    async def setup(cls, *args, **kwargs):
        """Setup init variables and session."""
        raise NotImplementedError()

    @classmethod
    @async_retry(ClientError, tries=2, tries_interval=1, total_timeout=4, show_logs=True, _logger=logger.debug)
    @final
    async def _request(cls, method: str, request_url: str, **kwargs) -> ResponseType:
        logger.debug(f'_request: {request_url}')
        async with cls._session.request(method=method, url=request_url, **kwargs) as response:
            return await cls._response(response)

    @classmethod
    async def _response(cls, response: ClientResponse) -> ResponseType:
        """Method for process response to dict.

        Notice: Redefine method for another format response.
        """
        logger.debug(f'_response: {response.status}')
        if response.status in cls._correct_response_statuses:
            try:
                return await response.json()
            except AttributeError:
                pass
        else:
            logger.debug(f'_response: {response}')
            try:
                logger.debug(f'_response: {await response.json()}')
            except AttributeError:
                pass
            logger.debug(f'_response: {await response.text()}')

    @classmethod
    @final
    async def shutdown(cls) -> None:
        """Method for grace full shutdown."""
        # For a ClientSession with SSL, the application must wait a short duration before closing
        # Wait 250 ms for the underlying SSL connections to close
        await asyncio.sleep(0.250)
        await cls._session.close()
