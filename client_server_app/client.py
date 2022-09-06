import argparse
import json
import socket
import sys
import threading

from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR, SENDER, MESSAGE, MESSAGE_TEXT, EXIT, DESTINATION
from common.utils import send_message, get_message
import time
import log.configs.client_log_config
import logging
from decorators import log

LOGGER = logging.getLogger('client_logger')


@log
def create_exit_message(account_name):
    """
    Function creates an exit message for the server, returns a python dict object
    :param account_name: name of the client
    :return: dict with message
    """
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


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
def message_from_server(sock, my_username):
    """
    Function processes the messages from the other users that we receive from the server
    :param sock: Socket object from whom we get the message
    :param my_username: Username of the client
    :return:
    """
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                    and DESTINATION in message and MESSAGE_TEXT in message \
                    and message[DESTINATION] == my_username:
                print(f'\nWas received a message from {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                LOGGER.debug(f'\nWas received a message from {message[SENDER]}:'
                             f'\n{message[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'\nWas received an incorrect message {message} ')
        except OSError:
            LOGGER.error('The connection was lost!')
            break


@log
def create_message(sock, account_name='Guest'):
    """
    Function asks for the text of the message and returns it. Client can be stopped by typing 'close'
    :param sock: Client that is sending the message
    :param account_name:
    :return: message as dict python object
    """
    to_user = input('Please type the user that must receive the message: ')
    message = input('Please type the message that you want to send: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Made message dict: {message_dict}')
    try:
        send_message(message_dict, sock)
        LOGGER.info(f'Was sent a message to the user {to_user}')
    except:
        LOGGER.critical('Was lost the connection with the server!')
        sys.exit(1)


@log
def user_interactive(sock, username):
    """
    Function interacts with the user, asks commands and sends messages
    :param sock:
    :param username:
    :return:
    """
    print_help()
    while True:
        command = input('Please enter a command: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(create_exit_message(username), sock)
            print('Logging out.')
            LOGGER.info('Client exited!.')
            time.sleep(0.5)
            break
        else:
            print('Command not found.Try help to see the commands.')


def print_help():
    """Function helps the client to enter a correct command"""
    print('Commands:')
    print('message - Send a message.')
    print('help - see all the commands')
    print('exit - exit the program')


@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Trying to run the server from an invalid port: {server_port}. '
            f'Port must be between 1024 and 65535. Client stopped.')
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    # getting the parameters from the command line
    print('Client module in console messenger.')
    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Please enter the username: ')

    LOGGER.info(f'Was started a client with parameters: server address: {server_address}, '
                f'port: {server_port}, client name: {client_name}')

    # starting the socket
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))

        message_to_the_server = create_presence(client_name)
        send_message(message_to_the_server, transport)
        response = process_presence_response(get_message(transport))
        LOGGER.info(f'Connected to the server. Response from server: {response}')
    except (ValueError, json.JSONDecodeError):
        LOGGER.error('Was not possible to decode the message from the server! ')
        sys.exit(1)

    else:
        # thread to get the messages
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        # thread to send the messages and interact with client
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        LOGGER.debug('processes started')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
