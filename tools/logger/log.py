import logging
import os


SPLITTER_LOG_DIR = "/tmp/"
if os.environ.get('SPLITTER_LOG_DIR'):
    SPLITTER_LOG_DIR = os.environ.get('SPLITTER_LOG_DIR')


class SplitterLogger:
    def __init__(self, name="splitter", level=logging.INFO):
        """ Initialize logger """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create stream handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        # Set logging format
        formatter = logging.Formatter('%(asctime)s-%(pathname)s[line:%(lineno)d]-%(levelname)s: %(message)s')
        ch.setFormatter(formatter)
        # Add handler to logger
        self.logger.addHandler(ch)

    def debug(self, msg):
        self.logger.debug(msg, stacklevel=2)

    def info(self, msg):
        self.logger.info(msg, stacklevel=2)

    def warning(self, msg):
        self.logger.warning(msg, stacklevel=2)

    def error(self, msg):
        self.logger.error(msg, stacklevel=2)

    def critical(self, msg):
        self.logger.critical(msg, stacklevel=2)
