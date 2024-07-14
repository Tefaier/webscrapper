class HolderNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class TargetNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class UnsupportedArgumentsException(Exception):
    def __init__(self, message):
        self.message = message


class CommandException(Exception):
    def __init__(self, message):
        self.message = message


class MaxOpeningTimeExceeded(Exception):
    def __init__(self, message):
        self.message = message
