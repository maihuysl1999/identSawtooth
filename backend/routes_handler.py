import json
import re
import asyncio
from json import JSONDecodeError


from identification.routes_handler import identityHandler
from utils.logging import get_logger
from utils.response import *
from constants import regex, message, role

_LOGGER = get_logger(__name__)


class RouteHandler:
    def __init__(self, database):
        self._ident_handler = identityHandler(database)

    async def login(self, request):
        _LOGGER.info("Logging")
        body = await decode_request(request)
        required_fields = ["username", "password"]
        validate_fields(required_fields, body)
        response = await self._ident_handler.login(body)
        return response

    async def create_user(self, request):
        _LOGGER.info("Create new user")
        body = await decode_request(request)
        required_fields = ["username", "password", "full_name", "email", "phone"]
        validate_fields(required_fields, body)
        response = await self._ident_handler.create_user(body)
        return response
    
    async def get_owner_info(self, request,user_info):
        _LOGGER.info("Get user info")
        user_id=user_info["user_id"]
        response = await self._ident_handler.get_owner_info(user_id)
        return response
    
    async def share_info(self, request, user_info):
        _LOGGER.info("share info")
        body = await decode_request(request)
        required_fields = ["receiver_email"]
        validate_fields(required_fields, body)
        user_id=user_info["user_id"]
        response = await self._ident_handler.share_info(body, user_id)
        return response

    async def get_shared_info(self, request, user_info):
        _LOGGER.info("get shared info")
        body = await decode_request(request)
        required_fields = ["owner_email"]
        validate_fields(required_fields, body)
        user_id=user_info["user_id"]
        response = await self._ident_handler.get_shared_info(body, user_id)
        return response

async def decode_request(request):
    try:
        return await request.json()
    except JSONDecodeError:
        raise ApiBadRequest('Improper JSON format')

def validate_fields(required_fields, body):
    for field in required_fields:
        if body.get(field) is None:
            raise ApiBadRequest(
                f"{field} parameter is required")
        elif field == 'username':
            if not re.match(regex.USERNAME_REGEX, body["username"]):
                raise ApiBadRequest(message.INVALID_USERNAME)
        elif field == 'password':
            if not re.match(regex.PASSWORD_REGEX, body["password"]):
                raise ApiBadRequest(message.INVALID_PASSWORD)
        elif field == 'email':           
            if not re.match(regex.EMAIL_REGEX, body["email"]) :
                raise ApiBadRequest(message.INVALID_EMAIL)
        elif field == 'full_name':
            if not re.match(regex.NAME_REGEX, body["full_name"]) :
                raise ApiBadRequest(message.INVALID_NAME)
        elif field == 'location':
            if not re.match(regex.LOCATION_REGEX, body["location"]):
                raise ApiBadRequest(message.INVALID_LOCATION)
        elif field == 'phone':
            if not re.match(regex.PHONE_REGEX, body["phone"]):
                raise ApiBadRequest(message.INVALID_PHONE)
        elif field == 'birthday':
            if not re.match(regex.DATE_REGEX, body["birthday"]):
                raise ApiBadRequest(message.INVALID_DATE)
