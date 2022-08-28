import json
import socket
import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR
from common.utils import send_message, get_message
import time
import log.configs.client_log_config
import logging

LOGGER = logging.getLogger('client_logger')


def create_presence(account_name='Guest'):
    """
    Function creates a presence message to send to the server
    :param account_name: By default the name is Guest
    :return: presence_message: Message that will be sent to the server, returns it as a python dict object
    """
    LOGGER.info(f'Creating presence message for the server with "account_name" = {account_name}')
    presence_message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.info(f'Final presence message for the server: "{presence_message}"')
    return presence_message


def process_response(response):
    """
    Gets the response from the server and returns the response code
    :param response: Message from the server as a python dict object
    :return: result: Response code from the response message from the server
    """
    LOGGER.info(f'Processing response from the server. Response: "{response}"')
    if isinstance(response, dict):
        if response[RESPONSE] == 200:
            LOGGER.info('Response is okay. Returned 200: OK')
            return '200 : OK'
        LOGGER.critical('Response from the server 400!')
        return f'400: {response[ERROR]}'


def main():
    """
    Function to run the client socket, getting the params from the command line, if there are not params, we give
    default variables
    Example for the command line:
    client.py 192.168.0.104 6565
    :return:
    """
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        LOGGER.error('The number of the port must be in the diapason from 1024 to 65535! ')
        print("The number of the port must be in the diapason from 1024 to 65535! ")
        sys.exit(1)

    # starting the socket

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))

    message_to_the_server = create_presence()
    # message_to_the_server = create_presence('Carlos') # Bad request account_name != 'Guest'
    send_message(message_to_the_server, transport)
    try:
        response = process_response(get_message(transport))
        LOGGER.info(f'Response from server: {response}')
    except (ValueError, json.JSONDecodeError):
        LOGGER.error('Was not possible to decode the message from the server! ')


if __name__ == '__main__':
    main()
