import logging
from logging import Logger, Formatter
from typing import List


class LogWriter:
    def __init__(self, full_path: str):
        self.handler = logging.FileHandler(full_path, encoding="utf-8")
        self.handler.setFormatter(
            Formatter("%(asctime)s.%(msecs)03d %(levelname)s - %(name)s: %(message)s", datefmt="%H:%M:%S")
        )
        self.loggers: List[Logger] = []

    def get_logger(self, name: str) -> Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.handler)
        self.loggers.append(logger)

        return logger

    def __del__(self):
        for logger in self.loggers:
            logger.removeHandler(self.handler)
        self.handler.flush()
        self.handler.close()
