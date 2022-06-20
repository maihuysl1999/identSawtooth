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
# -----------------------------------------------------------------------------

import hashlib
import logging

from sawtooth_sdk.protobuf import batch_pb2
from sawtooth_sdk.protobuf import transaction_pb2

from .addressing import addresser
from .protobuf import payload_pb2

LOGGER = logging.getLogger(__name__)


def make_create_user_transaction(
    transaction_signer, batch_signer, timestamp, 
    id, 
    email, 
    full_name, 
    location, 
    phone
):

    user_address = addresser.get_user_address(id)
    
    inputs = [user_address]
    outputs = [user_address]

    action = payload_pb2.CreateUserAction(
        id=id,
        email=email,
        full_name=full_name,
        location=location,
        phone=phone
    )

    payload = payload_pb2.DappPayload(
        action=payload_pb2.DappPayload.CREATE_USER,
        create_user=action,
        timestamp=timestamp
    )
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer
    )

def make_update_user_transaction(
    transaction_signer, batch_signer, timestamp, 
    id, 
    email, 
    full_name, 
    location, 
    phone
):

    user_address = addresser.get_user_address(id)
    
    inputs = [user_address]
    outputs = [user_address]

    action = payload_pb2.UpdateUserAction(
        id=id,
        email=email,
        full_name=full_name,
        location=location,
        phone=phone
    )

    payload = payload_pb2.DappPayload(
        action=payload_pb2.DappPayload.UPDATE_USER,
        update_user=action,
        timestamp=timestamp
    )
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer
    )

def _make_batch(payload_bytes,
                inputs,
                outputs,
                transaction_signer,
                batch_signer):

    transaction_header = transaction_pb2.TransactionHeader(
        family_name=addresser.FAMILY_NAME,
        family_version=addresser.FAMILY_VERSION,
        inputs=inputs,
        outputs=outputs,
        signer_public_key=transaction_signer.get_public_key().as_hex(),
        batcher_public_key=batch_signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=hashlib.sha512(payload_bytes).hexdigest())
    transaction_header_bytes = transaction_header.SerializeToString()

    transaction = transaction_pb2.Transaction(
        header=transaction_header_bytes,
        header_signature=transaction_signer.sign(transaction_header_bytes),
        payload=payload_bytes)

    batch_header = batch_pb2.BatchHeader(
        signer_public_key=batch_signer.get_public_key().as_hex(),
        transaction_ids=[transaction.header_signature])
    batch_header_bytes = batch_header.SerializeToString()

    batch = batch_pb2.Batch(
        header=batch_header_bytes,
        header_signature=batch_signer.sign(batch_header_bytes),
        transactions=[transaction])
    
    batch_list = batch_pb2.BatchList(batches=[batch])
    batch_bytes = batch_list.SerializeToString()

    return batch, batch_bytes