# logger/request_logger.py
from loguru import logger

class AppLogger:
    def __init__(self, log_file="app.log"):
        self.log_file = log_file
        self.configure_logger()

    def configure_logger(self):
        logger.add(
            self.log_file,
            level="INFO",
            rotation="60 minute",
            compression="zip"
        )

    def get_logger(self):
        return logger