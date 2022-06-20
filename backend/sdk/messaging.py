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

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import secp256k1
import time
import requests


from .errors import ValidatorError
from .transaction_creation import make_create_user_transaction
from .transaction_creation import make_update_user_transaction

class Messenger(object):
    def __init__(self, validator_url):
        # self._connection = Connection(validator_url)
        self._context = create_context('secp256k1')
        self._crypto_factory = CryptoFactory(self._context)
        self._batch_signer = self._crypto_factory.new_signer(
            self._context.new_random_private_key())

    def open_validator_connection(self):
        self._connection.open()

    def close_validator_connection(self):
        self._connection.close()

    def get_new_key_pair(self):
        private_key = self._context.new_random_private_key()
        public_key = self._context.get_public_key(private_key)
        return public_key.as_hex(), private_key.as_hex()

    def send_create_user_transaction(self, private_key, timestamp,         id,         email,         full_name,         location,         phone):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch, batch_bytes = make_create_user_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            timestamp=timestamp,
            id=id,
            email=email,
            full_name=full_name,
            location=location,
            phone=phone
            )
        self._send_and_wait_for_commit(batch_bytes)
        return batch

    def send_update_user_transaction(self, private_key, timestamp,         id,         email,         full_name,         location,         phone):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch, batch_bytes = make_update_user_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            timestamp=timestamp,
            id=id,
            email=email,
            full_name=full_name,
            location=location,
            phone=phone
            )
        self._send_and_wait_for_commit(batch_bytes)
        return batch


    def _send_and_wait_for_commit(self, batch):
        response = requests.post(url='http://165.232.172.15:32002/batches', 
                                 data=batch,
                                 headers={'Content-Type': 'application/octet-stream'})
        response_json = response.json()
        if 'link' in response_json:
            count = 0
            max_try = 10
            while count < max_try:
                status = requests.get(url=response_json["link"])
                status = status.json()["data"][0]["status"]
                if status == "PENDING":
                    count = count + 1
                    time.sleep(2)
                elif status == "COMMITTED":
                    return
                elif status == "INVALID":
                    break
            raise ValidatorError(f"The transaction is {status}")
        else:
            raise ValidatorError(response_json["error"]["title"])

            