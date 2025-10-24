import logging
from logging import Logger, Formatter


class LogWriter:
    def __init__(self, full_path: str):
        self.handler = logging.FileHandler(full_path)
        self.handler.setFormatter(
            Formatter("%(asctime)s %(levelname)s - %(name)s: %(message)s", datefmt="%H:%M:%S,%f")
        )

    def get_logger(self, name: str) -> Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.handler)

        return logger
