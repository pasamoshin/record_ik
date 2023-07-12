import sys
import json
import pyaudio
from threading import Thread
from configparser import ConfigParser
from log_entry import log_entry
from vosk import Model, KaldiRecognizer
from sounddevice import query_devices
from record_mic import RecordMic
from saved_record import *
    


def read_config():
    '''Чтение файла конфигурации, запись переменных конфигураций. '''
    config = ConfigParser()
    config.read("settings.ini", encoding="utf-8")
    return config


def create_var(config):
    '''Формирование всех необходимых для работы переменных в единый словарь. '''
    dirname = path.dirname(__file__)  # определение местоположения программы
    path_model = config["global_settings"]["PATH_MODEL"]
    # Если путь к модели не полный, а относительный (относительно местоположения программы)
    if path_model[1] != ':':
        path_model = path.join(dirname, path_model)
    # log_entry(f"Путь к модели: {path_model}")


    save_path = config["global_settings"]["SAVE_PATH"]
    save_path = create_save_dir(save_path)
  

    global_config = {
                     "PATH_MODEL":path_model,
                     "WORK_DIR":config["global_settings"]["WORK_DIR"],
                     "SAVE_PATH":config["global_settings"]["SAVE_PATH"],
                     "RECORD_LENGTH":int(config["global_settings"]["RECORD_LENGTH"]),
                     "control_ram":config["global_settings"]["control_ram"],
                     "max_ram":int(config["global_settings"]["max_ram"]),
                     }

    config_micr = {
                   "FORMAT":pyaudio.paInt16,
                   "ID_MIC":config["settings_mic"]["ID_MIC"],
                   "MIC_RATE":int(config["settings_mic"]["RATE"]),
                   "MIC_CHUNK":int(config["settings_mic"]["CHUNK"]),
                   "MIC_CHANNELS":int(config["settings_mic"]["CHANNELS"])
                   }
    
    config_speak = {
                    "DYN_RATE":int(config["settings_speak"]["RATE"]),
                    "ID_DYN":config["settings_speak"]["ID_DYN"],
                    "MODE":int(config["settings_speak"]["MODE"])
                    }
    
    # config_network = {
    #                   "network_control":config["network_settings"]["network_control"] 
    #                 }

    return global_config, config_micr, config_speak

# Объявление переменных
config_file = read_config()
global_config, config_mic, config_speak = create_var(config_file)


def start_model(path_model):
    '''Выгрузка языковой модели для распознавания слов в ОЗУ'''
    try:
        model = Model(path_model)
    except Exception as e:
        log_entry(e)
        log_entry("Модель не запустилась")
        sys.exit()
    log_entry("Модель запущена")
    return model


def choose_mic(id_mic):
    '''Функция выбора микрофона'''
    s = query_devices()
    log_entry(s)
    p = pyaudio.PyAudio()
    try:
        default_device = p.get_default_input_device_info()['index']
        log_entry(f"ID микрофона по умолчанию: {default_device}")   
    except Exception as e:
        log_entry(e, 'Установите микрофон по умолчанию в ОС или введите корректный индекс устройства в setting.ini')
        sys.exit()
    if id_mic == 'default':
        id_mic = default_device
        log_entry(f'Выбран микрофон по умолчанию id: {default_device}')
    else:
        try:
            id_mic = int(id_mic)
        except ValueError:
            log_entry('Неверный ID микрофона. Укажите в setting.ini ID микрофона')
            sys.exit()
        log_entry(f'Выбран микрофон ID: {id_mic}. Рекомендуется перенастроить микрофон на по умолчанию')
    return id_mic

        
def config_stream(conf_mic):
    '''Функция конфигурации парамтеров для стрима'''
    p = pyaudio.PyAudio()
    stream = p.open(
            format=conf_mic['FORMAT'],
            channels=conf_mic['MIC_CHANNELS'],
            rate=conf_mic['MIC_RATE'],
            input=True,
            input_device_index=conf_mic['ID_MIC'],
            frames_per_buffer=conf_mic['MIC_CHUNK']
        )
    return stream

def go_stream(stream, mic_rate, model): 
    '''Запуск стрима и расознавателя'''
    rec = KaldiRecognizer(model, mic_rate) # Запуск распознавателя
    stream.start_stream() # Запуск стрима
    log_entry('Расознавание определено, стрим запущен')
    return rec, stream


def listen_stream(rec, stream):
    ''' Функция распознавания слов. Главная функция программы. От нее все идет. '''
    log_entry('Запущено чтение и распознавание стрима')
    while True:
        if global_config["control_ram"] == "on":
            ram_control()
        try:
            data = stream.read(4000, exception_on_overflow=False)
        except Exception as e:
            log_entry(e, 'Был выключен прослушиваемый микрофон, ПО будет перезапущено')
            sys.exit()
        rec_accept = rec.AcceptWaveform(data)
        if rec_accept:
            answer = json.loads(rec.Result())
            if answer['text'] != '':
                log_entry(f"Распознание: {answer['text']}")
                record()



def record_micro():
    '''Функция записи микрофона в dump.'''
    r = RecordMic(global_config["RECORD_LENGTH"], config_mic)
    global NAME_FILE_MIC
    name = creat_name_files()
    date = name[0]
    name_arm = name[1]
    NAME_FILE_MIC = date + name_arm + "_mic.wav"
    try:
        r.record_mic(path.join(f'{global_config["WORK_DIR"]}/dump/trf/0', NAME_FILE_MIC))
    except Exception as e:
        log_entry(e)
        kill_all()

   


def record_speak():
    global NAME_FILE_SPEAK
    global date_rec 
    '''Функция записи динамика в dump.'''
    if config_speak['MODE'] == 0:
        from record_dyn import RecordDyn
        r = RecordDyn(global_config["RECORD_LENGTH"], config_speak)
        name = creat_name_files()
        date_rec = name[0]
        name_arm = name[1]
        NAME_FILE_SPEAK = date_rec + name_arm + "_dyn.wav"
        r.record_dyn(path.join(f'{global_config["WORK_DIR"]}/dump/trf/0', NAME_FILE_SPEAK))
    elif config_speak['MODE'] == 1:
        from record_dyn_mode_1 import RecordDyn_1
        r = RecordDyn_1(global_config["RECORD_LENGTH"], config_speak)
        name = creat_name_files()
        date_rec = name[0]
        name_arm = name[1]
        NAME_FILE_SPEAK = date_rec + name_arm + "_dyn.wav"
        r.record_dyn(path.join(f'{global_config["WORK_DIR"]}/dump/trf/0', NAME_FILE_SPEAK))





def work_file():
    name_trf = create_trf(NAME_FILE_MIC, NAME_FILE_SPEAK)
    date = str(date_rec[:10] + ' ' + date_rec[11:])
    name_ssn = create_ssn(date)
    creat_file_contents(name_ssn, name_trf)
    create_ez()
    del_dump()


def record():
    ''' Функция распределения одновременной записи микрофона и динамика'''
    del_dump()
    create_trf_dir()

    t1 = Thread(target=record_micro)
    t2 = Thread(target=record_speak)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    t3 = Thread(target=work_file)
    t3.start()



def ram_control():
    '''Контроль заполнения ОЗУ'''
    from memory_profiler import memory_usage
    a = memory_usage()
    if a[0] > global_config['max_ram']:
        kill_all()



def main():
    #Очищаем дамп в случае наличия невыгруженных данных, для избежания конфликта
    del_dump()  
    # Проверка/создание директории для сохранения файлов ez
    create_save_dir(global_config["SAVE_PATH"])
    # Создание каталога для промежуточных файлов
    create_dump_dir()


    # Выбор микрофона согласно settings.ini
    config_mic["ID_MIC"] = choose_mic(config_mic["ID_MIC"])
    # Запуск модели, выгрузка ее в ОЗУ
    model = start_model(global_config["PATH_MODEL"])
    # Формирование конфига стрима
    stream = config_stream(config_mic)
    # Запуск стрима и расознавателя
    rec, stream = go_stream(stream, config_mic["MIC_RATE"], model)
    # Прослушивание стрима
    listen_stream(rec, stream)


def kill_all():
    '''Убивает выполнение процесса в случае ошибки'''
    import psutil
    from os import getpid
    current_system_pid = getpid()
    ThisSystem = psutil.Process(current_system_pid)
    ThisSystem.terminate()



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_entry(e)
    finally:
        kill_all()


