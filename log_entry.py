from configparser import ConfigParser
from os import path, remove
from datetime import datetime
from net_client import send_message

config = ConfigParser()
config.read("settings.ini")
DEBUG_MODE = config["global_settings"]["DEBUG_MODE"]
WORK_DIR = config["global_settings"]["WORK_DIR"]


def create_time():
    '''Создание времени для логирования'''
    now = datetime.now()
    create_time = str(now.strftime("%Y-%m-%d %H:%M:%S"))
    return create_time


def append_in_file(message, atr_file):
    time = create_time()
    log_str = f"{time} {message}"
    with open(f"{WORK_DIR}/log.txt", atr_file, encoding='utf-8') as file:
        file.write(f'\n{log_str}')
    send_message(log_str)   

def log_entry(*message):
    if DEBUG_MODE == "on":
        print(*message)
    check_file = path.isfile(f"{WORK_DIR}\log.txt")
    if check_file:
        log_file = path.join(f'{WORK_DIR}\log.txt')
        if path.getsize(log_file) > 5242880:
            remove(log_file)

            for val in message:
                append_in_file(val, 'w')
        else:
            for val in message:
                append_in_file(val, 'a')
    else:
       for val in message:
        append_in_file(val, 'w')

if __name__ == '__main__':
    log_entry()

