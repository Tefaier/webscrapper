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


class MaxOpeningTimeExceededException(Exception):
    def __init__(self, message):
        self.message = message


class NextChapterNotReachedException(Exception):
    def __init__(self, message):
        self.message = message


class LinkException(Exception):
    def __init__(self, message):
        self.message = message
