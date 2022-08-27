from typing import Any

from fastapi import APIRouter, Query, Body
from starlette.requests import Request


router = APIRouter()

# https://developer.squareup.com/docs/oauth-api/overview
# https://developer.squareup.com/docs/orders-api/how-it-works#orders-objects-and-datatypes
# https://developer.squareup.com/docs/locations-api


@router.get("/oauth2/auth-url")
async def get_auth_link(
        request: Request,
) -> Any:
    """Method for receive auth url for Seller."""
    square_interface = request.app.state.square_interface
    settings = request.app.state.settings
    client_id = settings.SQUARE.APPLICATION_ID
    auth_url = await square_interface.get_oauth_authorize(client_id=client_id)
    data = {'auth_url': auth_url}
    return data


@router.get("/oauth2/callback")
async def obtain_token(
        request: Request,
        code: str = Query(..., description='authorization code'),
) -> Any:
    """Provide the code in a request to the Obtain Token endpoint."""
    settings = request.app.state.settings
    square_interface = request.app.state.square_interface
    data = await square_interface.obtain_token(
        client_id=settings.SQUARE.APPLICATION_ID,
        client_secret=settings.SQUARE.APPLICATION_SECRET,
        code=code,
        grant_type='authorization_code'
    )
    # {
    #   "access_token": "ACCESS_TOKEN",
    #   "token_type": "bearer",
    #   "expires_at": "2006-01-02T15:04:05Z",
    #   "merchant_id": "MERCHANT_ID",
    #   "refresh_token": "REFRESH_TOKEN"
    # }
    return data
