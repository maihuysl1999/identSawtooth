import base64
import hashlib
import os
from datetime import datetime, timedelta
from settings import config
import jwt

EXPIRED_TIME = 365

def encode_jwt(user):
    user["exp"] = datetime.utcnow() + timedelta(days=EXPIRED_TIME)
    token = jwt.encode(user, key=config["jwt_key"], algorithm="HS256", )
    return token

def sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    m = hashlib.sha1()
    m.update(data)
    return m.hexdigest()