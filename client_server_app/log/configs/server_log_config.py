import logging
from logging.handlers import TimedRotatingFileHandler
from common.variables import SERVER_LOGGING_LEVEL
import os
import sys

LOGGER = logging.getLogger('server_logger')

FORMATTER = logging.Formatter("%(asctime)s  %(levelname)s  %(module)s  %(message)s ")

PATH = os.path.abspath(os.path.join(os.path.dirname('settings.py'), os.path.pardir))
if __name__ != '__main__':
    PATH = os.path.join(PATH, 'client_server_app/log')
PATH = os.path.join(PATH, 'logs')
log_file_name = os.path.join(PATH, 'server.log')

LOG_FILE = TimedRotatingFileHandler(log_file_name, encoding='utf-8', interval=1, when='midnight')
LOG_FILE.setFormatter(FORMATTER)

STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setLevel(SERVER_LOGGING_LEVEL)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(SERVER_LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Test_final')
