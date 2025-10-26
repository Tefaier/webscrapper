from enum import Enum


class RequestStatus(Enum):
    CREATED = 0
    ACTIVE = 1
    SUCCESS = 2
    FAILED = 3
