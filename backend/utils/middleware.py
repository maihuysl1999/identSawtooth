from aiohttp.web import middleware
import jwt
from utils.response import ApiUnauthorized
from utils.logging import get_logger

_LOGGER = get_logger(__name__)

@middleware
async def authorized(request, handler):
    if request.method != "OPTIONS":
        if request.path == '/v1/login' or request.path == '/v1/users':
            resp = await handler(request)
            return resp
        else:
            token = request.headers.get("AUTHORIZATION")
            if token is None:
                raise ApiUnauthorized("No auth token provided!")

            token_prefixes = ("Bearer", "Token")
            for prefix in token_prefixes:
                if prefix in token:
                    token = token.partition(prefix)[2].strip()
            try:
                user_info = jwt.decode(token, request.app["config"]["jwt_key"], algorithms=['HS256'])
            except:
                raise ApiUnauthorized('Invalid auth token')
            resp = await handler(request, user_info)
            return resp
    else:
        resp = await handler(request)
        return resp
