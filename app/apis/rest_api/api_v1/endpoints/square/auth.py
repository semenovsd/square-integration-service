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
        client_id: str = Query(..., description='client_id. The ID that is associated with an application using the '
                                                'OAuth process. This is a public variable and is called the '
                                                'Application ID in the Developer Dashboard on the OAuth page.')
) -> Any:
    """Method for receive auth url for Seller."""
    square_interface = request.app.state.square_interface
    auth_url = await square_interface.get_oauth_authorize(client_id=client_id)
    data = {'auth_url': auth_url}
    return data


@router.post("/oauth2/obtain-token")
async def obtain_token(
        request: Request,
        client_id: str = Body(...),
        client_secret: str = Body(...),
        code: str = Body(...),
) -> Any:
    """Method for receive auth url for Seller."""
    square_interface = request.app.state.square_interface
    auth_url = await square_interface.get_oauth_authorize(client_id=client_id)
    data = {'auth_url': auth_url}
    return data
