import asyncio
from utils.mail import  otp_code, send_email
from utils.response import success, ApiBadRequest, ApiInternalError
from utils.logging import get_logger
from aiohttp import web
import datetime
import os
from constants import plan, role, message
from utils import security
import pyshorteners
from sdk.handler import Handler

_LOGGER = get_logger(__name__)

class identityHandler:
    def __init__(self, database):
        self.__database = database
        self.handler = Handler()
   
    async def login(self, body):
        username = body["username"]
        password = body["password"]
        password = security.sha(password)

        user = await self.__database.get_user(username=username, password=password)
        if not user:
            return ApiBadRequest(message.WRONG_USERNAME_PASS)
        if not user["active"]:
            return ApiBadRequest(message.INACTIVE)
        
        payload = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email":user["email"],
        }
        token = security.encode_jwt(payload).decode('utf-8')
        return success({
            "message": message.LOGIN_SUCCESS,
            "token": token,
            "user_id": payload["user_id"],
            "user":user
        })

    async def create_user(self, new_user):
        user = await self.__database.get_user(username=new_user["username"])
        if user:
            return ApiBadRequest(message.EXISTING_USERNAME)
        user = await self.__database.get_user(email=new_user["email"])
        if user:
            return ApiBadRequest(message.EXISTING_EMAIL)

        public_key, private_key = self.handler.gen_key_pair()

        user_id = await self.__database.create_user({
            "username": new_user["username"],
            "password": security.sha(new_user["password"]),
            "email": new_user["email"],
            "created_date": str(datetime.datetime.now()),
            "active": True,
            "privateKey": private_key,
            "publicKey": public_key,
        })

        txid = self.handler.create_user(user_id,new_user["email"], new_user["full_name"], new_user["location"], new_user["phone"], private_key, public_key)

        modification={}
        modification["txid"]=txid["data"]["txid"]
        user_id = await self.__database.update_user(user_id, modification)

        return success({
            "message": message.ADD_USER,
            "user_id": user_id
        })

    async def get_owner_info(self,user_id):
        user = await self.__database.get_user( _id=user_id)
        if not user:
            return ApiBadRequest(message.WRONG_USERNAME_PASS)
        if not user["active"]:
            return ApiBadRequest(message.INACTIVE)
        
        user_info = self.handler.get_user(user_id)
    
        return success({
            "message": "Get User Info successful",
            "user": user_info["data"]["user"]
        }) 

    async def share_info(self,body,user_id):
        user = await self.__database.get_user( _id=user_id)
        if not user:
            return ApiBadRequest(message.WRONG_USERNAME_PASS)
        if not user["active"]:
            return ApiBadRequest(message.INACTIVE)

        receiver = await self.__database.get_user(email=body["receiver_email"])
        if not receiver:
            return ApiBadRequest(message.USER_NOT_FOUND)
        if not receiver["active"]:
            return ApiBadRequest(message.INACTIVE)

        shared_info = await self.__database.get_shared_info(owner_id=user["user_id"], receiver_id=receiver["user_id"])
        if shared_info:
            return ApiBadRequest(message.SHARED_INFO)
        
        shared_id = await self.__database.create_shared_info({
            "owner_id" : user_id,
            "receiver_id" : receiver["user_id"],
        })
    
        return success({
            "message": "share information for email " + receiver["email"] + " successful",
            "shared_id" : shared_id
        }) 

    async def get_shared_info(self, body, user_id):
        user = await self.__database.get_user( _id=user_id)
        if not user:
            return ApiBadRequest(message.WRONG_USERNAME_PASS)
        if not user["active"]:
            return ApiBadRequest(message.INACTIVE)
        
        owner_info = await self.__database.get_user( email=body["owner_email"])
        if not owner_info:
            return ApiBadRequest(message.USER_NOT_FOUND)
        if not owner_info["active"]:
            return ApiBadRequest(message.INACTIVE)

        shared_info = await self.__database.get_shared_info(owner_id=owner_info["user_id"], receiver_id=user["user_id"])
        if not shared_info:
            return ApiBadRequest(message.NOT_BEEN_SHARED)
        
        shared_info = self.handler.get_user(shared_info["owner_id"])

        return success({
            "message": "Get Shared info successful",
            "user": shared_info["data"]["user"]
        }) 
