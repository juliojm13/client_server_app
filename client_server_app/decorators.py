import sys
import logging
import log.configs.client_log_config
import log.configs.server_log_config
import inspect

# метод определения модуля, источника запуска.
# Метод find () возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке.
# Если его не найдено, - возвращает -1.
# os.path.split(sys.argv[0])[1]
if sys.argv[0].find('client') == -1:
    # если не клиент то сервер!
    LOGGER = logging.getLogger('server_logger')
else:
    # не сервер, то клиент
    LOGGER = logging.getLogger('client_logger')


def log(func_to_log):
    def log_saver(*args, **kwargs):
        ret = func_to_log(*args, **kwargs)
        LOGGER.debug(f'Was called the function "{func_to_log.__name__}" '
                     f'with arguments: {args} {kwargs} '
                     f'from the module:  {func_to_log.__module__} and was returned {ret}.'
                     f'The function was called from the function '
                     f'"{inspect.stack()[1][3]}"', stacklevel=2)
        return ret

    return log_saver
