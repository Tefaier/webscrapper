from enum import Enum


class FileExtensions(Enum):
    def __init__(self, value: int, text_support: bool, image_support: bool):
        self._value_ = value
        self.text_support = text_support
        self.image_support = image_support

    TXT = 0, True, False
    DOCX = 1, True, True
    HTML = 2, True, True
