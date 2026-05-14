from collections.abc import Iterable
from enum import IntFlag

MAX_JS_SAFE_INTEGER = 2**53 - 1


class Permission(IntFlag):
    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    READ_MESSAGES = 1 << 10
    SEND_MESSAGES = 1 << 11
    MANAGE_MESSAGES = 1 << 13
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MOVE_MEMBERS = 1 << 24


ALL_PERMISSIONS = sum(permission.value for permission in Permission)


def merge_permissions(permissions: Iterable[Permission | int]) -> int:
    value = 0
    for permission in permissions:
        value |= int(permission)
    if value > MAX_JS_SAFE_INTEGER:
        raise ValueError("permission bitfield exceeds JavaScript safe integer range")
    return value


def has_permission(granted: int, required: Permission | int) -> bool:
    if granted & Permission.ADMINISTRATOR:
        return True
    required_value = int(required)
    return (granted & required_value) == required_value
