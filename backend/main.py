import sys
from aiohttp import web, ClientSession
import aiohttp_cors
from settings import config
from utils.middleware import authorized
from database import Database
from utils.logging import get_logger
from routes_handler import RouteHandler


_LOGGER = get_logger(__name__)

app = web.Application(middlewares=[authorized])
app['config'] = config

async def setup_service(app):
    try:
        app["database"] = Database(host=app["config"]["database"]["host"],
                                   port=app["config"]["database"]["port"],
                                   username=app["config"]["database"]["username"],
                                   password=app["config"]["database"]["password"],
                                   dbname=app["config"]["database"]["db_name"])

        await app["database"].connect()
        
        handler = RouteHandler(app["database"])   
        
        app.router.add_route("POST", "/v1/login", handler.login)
        
        app.router.add_route("POST", "/v1/users", handler.create_user)
        app.router.add_route("GET", "/v1/users/info",handler.get_owner_info)
        app.router.add_route("POST", "/v1/users/share",handler.share_info)
        app.router.add_route("POST", "/v1/users/sharedinfo",handler.get_shared_info)

        cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True, expose_headers="*", allow_headers="*",allow_methods="*"
                )
            },
        )

        for route in list(app.router.routes()):
            cors.add(route)
           
    except Exception as err:
        _LOGGER.debug(err)
        sys.exit(1)

app.on_startup.append(setup_service)
web.run_app(app)