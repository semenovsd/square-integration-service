import asyncio
from typing import final, Final, TypeVar, Tuple

from aiohttp import ClientSession, ClientTimeout, ClientError, ClientResponse
from loguru import logger

from services.utils.decorators import async_retry


ResponseType = TypeVar('ResponseType', dict, ClientResponse)


@final
class SquareInterface:
    # https://developer.squareup.com/docs/devtools/sandbox/overview
    _BASE_API_URL: Final[str] = 'https://connect.squareupsandbox.com'  # prod: https://connect.squareup.com
    _session: ClientSession = None
    _correct_response_statuses: Tuple[int] = (200, 201)

    @classmethod
    async def setup(cls,) -> None:
        cls._session = ClientSession(timeout=ClientTimeout(total=4))

    @classmethod
    @async_retry(ClientError, tries=2, tries_interval=2, total_timeout=10, show_logs=True, _logger=logger.debug)
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
                return await response.json(content_type=None)
            except (AttributeError, ValueError):
                return response
        else:
            logger.debug(f'_response: {response}')
            try:
                logger.debug(f'_response: {await response.json()}')
            except AttributeError:
                pass
            logger.debug(f'_response: {await response.text()}')

    @classmethod
    async def shutdown(cls) -> None:
        """Method for grace full shutdown."""
        # For a ClientSession with SSL, the application must wait a short duration before closing
        # Wait 250 ms for the underlying SSL connections to close
        await asyncio.sleep(0.250)
        await cls._session.close()

    @classmethod
    async def get_authorize_link(
            cls,
            client_id: str,
            scope: str = 'CUSTOMERS_WRITE CUSTOMERS_READ',
            locale: str = 'en-US',
            session: bool = False,
            state: str = '82201dd8d83d23cc8a48caf52b',
            **kwargs
    ) -> str | None:
        """Generate auth link."""
        # https://developer.squareup.com/docs/oauth-api/create-urls-for-square-authorization
        request_url = cls._BASE_API_URL + '/oauth2/authorize'
        params = dict(
            client_id=client_id,
            scope=scope,
            session=str(session),
            state=state,
            locale=locale,
            **kwargs
        )
        query_params = ''.join(f'{arg}={params[arg]}&' for arg in params)
        request_url = request_url + f'?{query_params}'
        return request_url

    @classmethod
    async def obtain_token(
            cls,
            client_id: str,
            client_secret: str,
            code: str,
            grant_type: str,
    ) -> dict | None:
        # https://developer.squareup.com/docs/oauth-api/create-urls-for-square-authorization
        method = 'POST'
        request_url = cls._BASE_API_URL + '/oauth2/token'
        headers = {'Content-Type': 'application/json', 'Square-Version': '2022-08-23'}
        payload = dict(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            grant_type=grant_type
        )
        response = await cls._request(method=method, request_url=request_url, headers=headers, json=payload)
        if isinstance(response, dict):
            return response
