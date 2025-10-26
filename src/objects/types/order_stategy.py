from enum import Enum


class OrderStrategy(Enum):
    """
    Strategies for ordering the combined list of elements.
    CONCAT: keep the order by concatenating lists in the order provided.
    BY_SOURCELINE: order across all items by their source line for Tag elements.
                   Non-Tag or Tag without a sourceline keep stable order after
                   those that have sourceline.
    """

    def __init__(self, value: int, public_name: str):
        self._value_ = value
        self.public_name = public_name

    CONCAT = 0, "concat"
    BY_SOURCELINE = 1, "by sourceline"
    BY_TYPE = 2, "by type"
