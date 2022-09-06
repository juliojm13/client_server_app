"""Variables for the project and default variables"""

# Default port for the socket
DEFAULT_PORT = 7777
# Default IP address for the client's connection
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Max queue of connections
MAX_CONNECTIONS = 5
# Max length of the message package in bytes
MAX_PACKAGE_LENGTH = 1024
# Encoding used in the project
ENCODING = 'utf-8'

# Principal keys for JIM protocol interaction
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# Other keys for JIM protocol interaction
PRESENCE = 'presence'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
RESPONSE = 'response'
ERROR = 'error'
SENDER = 'sender'
DESTINATION = 'destination'
EXIT = 'exit'

# Logging level for client logger and server logger
CLIENT_LOGGING_LEVEL = 10
SERVER_LOGGING_LEVEL = 10
