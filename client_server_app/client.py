import argparse
import json
import socket
import sys
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR, SENDER, MESSAGE, MESSAGE_TEXT
from common.utils import send_message, get_message
import time
import log.configs.client_log_config
import logging
from decorators import log

LOGGER = logging.getLogger('client_logger')


@log
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


@log
def process_presence_response(response):
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


@log
def message_from_server(message):
    """
    Function to process the clients messages that we receive from the server
    :param message: Message that was received
    :return:
    """
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        LOGGER.info(f'Received a message from the user '
                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(f'Was received an incorrect message: {message}')


@log
def create_message(sock, account_name='Guest'):
    """
    Function asks for the text of the message and returns it. Client can be stopped by typing 'close'
    :param sock: Client that is sending the message
    :param account_name:
    :return: message as dict python object
    """
    message = input('Please type the message that you wnat to send. Type \'close\' to stop working: ')
    if message == 'close':
        sock.close()
        LOGGER.info('Work was finished by users command.')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Returning message dict: {message_dict}')
    return message_dict


@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Trying to run the server from an invalid port: {server_port}. '
            f'Port must be between 1024 and 65535. Client stopped.')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        LOGGER.critical(f'An incorrect mode for the client was chosen {client_mode}, '
                        f'The existing modes are: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    # getting the parameters from the command line
    server_address, server_port, client_mode = arg_parser()

    LOGGER.info(f'Was started a client with parameters: server address: {server_address}, '
                f'port: {server_port}, client mode: {client_mode}')

    # starting the socket
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))

        message_to_the_server = create_presence()
        # message_to_the_server = create_presence('Carlos') # Bad request account_name != 'Guest'
        send_message(message_to_the_server, transport)
        response = process_presence_response(get_message(transport))
        LOGGER.info(f'Connected to the server. Response from server: {response}')
    except (ValueError, json.JSONDecodeError):
        LOGGER.error('Was not possible to decode the message from the server! ')
        sys.exit(1)

    else:
        if client_mode == 'send':
            print('Mode send. Client will send messages.')
        else:
            print('Mode listen. Client will receive messages. ')

        while True:
            if client_mode == 'send':
                try:
                    send_message(create_message(transport), transport)
                except:
                    LOGGER.error(f'The connection with the server {server_address} was lost!')
                    sys.exit(1)
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except:
                    LOGGER.error(f'The connection with the server {server_address} was lost!')
                    sys.exit(1)


if __name__ == '__main__':
    main()
