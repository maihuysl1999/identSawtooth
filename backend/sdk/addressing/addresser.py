import enum
import hashlib


FAMILY_NAME = 'IDENTDAPP-5FD6D'
FAMILY_VERSION = '1'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[:6]

USER_PREFIX = '00'


@enum.unique
class AddressSpace(enum.IntEnum):
    USER = 0
    OTHER_FAMILY = 100


def get_user_address(id):
    return NAMESPACE + USER_PREFIX + hashlib.sha512(
        id.encode('utf-8')).hexdigest()[:62]


def get_address_type(address):
    if address[:len(NAMESPACE)] != NAMESPACE:
        return AddressSpace.OTHER_FAMILY

    infix = address[6:8]

    if infix == '0':
        return AddressSpace.USER_PREFIX

    return AddressSpace.OTHER_FAMILY