from configparser import ConfigParser
import psutil
from time import sleep
import subprocess


def get_config(conf_file):
    """
    Returns the config object
    """
    config = ConfigParser()
    config.read(conf_file)
    return config

def start_rocord_ik():
    start_control_record_ik()
    start_control_filecopier()
    start_control_net_client_ric()
    sleep(10)


def start_control_record_ik():
    for proc in psutil.process_iter():
        if proc.name() == 'record_ik.exe':
            try:
                pid = proc.as_dict(attrs=['pid'])
                size_ram = proc.memory_info().rss/1024/1024
            except psutil.NoSuchProcess:
                pass
            else:
                if size_ram < 170:
                    ThisSystem = psutil.Process(pid['pid'])
                    ThisSystem.terminate()
                    sleep(3)
                    path = get_config('start_control_settings.ini')['path_program']['exe_path_record_ik']
                    subprocess.Popen(path)  
                return
    path = get_config('start_control_settings.ini')['path_program']['exe_path_record_ik']
    subprocess.Popen(path)
                

    
    
def start_control_filecopier():
    for proc in psutil.process_iter():
        if proc.name() == 'filecopier.exe':
            return
    try:
        path = get_config('start_control_settings.ini')['path_program']['exe_path_filecopier']
        subprocess.Popen(path)
    except:
        pass

def start_control_net_client_ric():
    for proc in psutil.process_iter():
        if proc.name() == 'net_client_ric.exe':
            return
    try:
        path = get_config('start_control_settings.ini')['path_program']['exe_path_net_client_ric']
        subprocess.Popen(path)
    except:
        pass
            

if __name__ == "__main__":
    while True:
        start_rocord_ik()
