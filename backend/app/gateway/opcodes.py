from enum import IntEnum


class Opcode(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    UPDATE_VOICE_STATE = 4
    VOICE_SIGNAL = 5
    REQUEST_GUILD_MEMBERS = 8
    HELLO = 10
    HEARTBEAT_ACK = 11
