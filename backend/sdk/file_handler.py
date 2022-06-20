import requests
import json
import os
from .errors import StorageServiceRequestError, SchemaError

V_STORAGE_URL = 'https://storage.v-chain.vn/v1'

def upload_file(parent_id, sdk_key, file_path):
    if os.path.isdir(file_path):
        raise SchemaError(f'File in {file_path} doesnt exist!')

    try:
        response = requests.request(
            method = "POST",
            url = f"{V_STORAGE_URL}/files/{parent_id}/upload?sdk_key={sdk_key}",
            data = {
                "shared": []
            },
            files = {
                "upload_file": (file_path.split('/')[-1], open(file_path, 'rb'))
            })

        return json.loads(response.content.decode("utf8"))
    except Exception as e:
        raise StorageServiceRequestError(f"Error while upload file {file_path}!")
    