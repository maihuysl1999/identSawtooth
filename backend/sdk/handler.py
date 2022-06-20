# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
import datetime
from json.decoder import JSONDecodeError
import time
import datetime
import json
import requests
import base64

from google.protobuf.json_format import MessageToJson
from .errors import BadRequest, InternalError, CommunicationError
# generated from **Protobuf**
from .protobuf import user_pb2
from .protobuf import payload_pb2
from .addressing import addresser

from jsonschema import validate
from jsonschema import ValidationError
from .messaging import Messenger

from .AES_encrypt import AESCipher
from .file_handler import upload_file


class Handler(object):
    def __init__(self):
        validator_url='http://165.232.172.15:32001'
        endpoint='http://165.232.172.15:32002'
        self._messenger = Messenger(validator_url)
        self.endpoint = endpoint
        self.sdk_key = 'be8ff0a8-5a25-4362-9758-68730481431a'
        self.data_folder_id = '62b011890505467dc0bad9bb'
    
    def trace(self, transaction_ids):
        result = self.get_data_blockchain(transaction_ids)
        return result

    def gen_key_pair(self):
        public_key, private_key = self._messenger.get_new_key_pair()
        return public_key, private_key

    def create_user(self, id, email, full_name, location, phone, private_key
        ,public_key):
        temp = {}
            
            
            
            
            
        
        batch = self._messenger.send_create_user_transaction(
            private_key=private_key,
            timestamp=get_time(),
            id=id,
    
            email=email,
    
            full_name=full_name,
    
            location=location,
    
            phone=phone
    
 
        )
        transaction_id = batch.transactions[0].header_signature
        return {
            "data": {
                "txid": transaction_id
            }
        }

    def update_user(self, id, email, full_name, location, phone, private_key
        ,public_key):
        temp = {}
            
            
            
            
            
        
        batch = self._messenger.send_update_user_transaction(
            private_key=private_key,
            timestamp=get_time(),
            id=id,
    
            email=email,
    
            full_name=full_name,
    
            location=location,
    
            phone=phone
    
 
        )
        transaction_id = batch.transactions[0].header_signature
        return {
            "data": {
                "txid": transaction_id
            }
        }

    def get_user(self, id):
        user_address = addresser.get_user_address(id)

        url = '{}/state/{}'.format(self.endpoint, user_address)
        response = requests.get(url)
        if response.status_code == 200:
            try:
                content = response.content
                content_json = content.decode('utf8').replace("'", '"')
                payload_bytes_response = json.loads(content_json)['data']
                container = user_pb2.UserContainer()
                container.ParseFromString(base64.b64decode(payload_bytes_response))
                json_data = json.loads(MessageToJson(container, preserving_proto_field_name=True))
                return {
                    "data": {
                        'user': json_data["entries"][0],
                    }
                }
            except:
                raise InternalError('Cannot decode the response')
        else:
            raise CommunicationError('Cannot get user with id={}'.format(id))

    def get_data_blockchain(self, transaction_ids):
        results = []
        for transaction_id in transaction_ids:
            url = '{}/transactions/{}'.format(self.endpoint, transaction_id)
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    transaction_dict = json.loads(response.content)
                    payload_string = transaction_dict['data']['payload']
                    data_model = payload_pb2.DappPayload()
                    data_model.ParseFromString(base64.b64decode(payload_string))
                    json_data = json.loads(MessageToJson(data_model, preserving_proto_field_name=True))
                    for key, value in json_data.items():
                        if key != "action" and key != "timestamp":
                            result = {}
                            for property_key, property_value in value.items():
                                split_name = property_key.split("__")
                                if len(split_name) == 1:
                                    result[split_name[0]] = property_value
                                else:
                                    current_level = result
                                    for index in range(len(split_name)):
                                        if index == len(split_name)-1:
                                            current_level[split_name[index]] = property_value
                                            break
                                        if split_name[index] not in current_level:
                                            current_level[split_name[index]] = {}
                                        current_level = current_level[split_name[index]]
                            results.append(result)
                except:
                    raise CommunicationError("Error to get data from blockchain")

        return results

def validate_fields(required_fields, body):
    for field in required_fields:
        if body.get(field) is None:
            raise BadRequest(
                "'{}' parameter is required".format(field))


def validate_types(schema, body):
    try:
        validate(instance=body, schema=schema)
    except ValidationError as e:
        string_array_error = str(e).split("\n")
        array = {"On instance","[","]","'",":"," "}
        for a in array:
            string_array_error[5] = string_array_error[5].replace(a,"")
        message = string_array_error[0]+" on field '"+ string_array_error[5] +"'"

        raise BadRequest(message)

def get_time():
    dts = datetime.datetime.utcnow()
    return round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)