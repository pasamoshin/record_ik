from configparser import ConfigParser
from datetime import datetime
from os import makedirs, path, listdir, remove, SEEK_END
import pathlib
from platform import node
import shutil
import sys
from log_entry import log_entry
import csv
from zipfile import ZipFile



config = ConfigParser()
config.read("settings.ini")
Ss_src = config["global_settings"]["Ss_src"]
arm_location = config["global_settings"]["arm_location"]
rec_length  = config["global_settings"]["RECORD_LENGTH"]
save_dir = config["global_settings"]["SAVE_PATH"]
WORK_DIR = config["global_settings"]["WORK_DIR"]
del config




def create_trf_dir():
    try:
        makedirs(f'{WORK_DIR}/dump/trf/0')
    except Exception as e:
        log_entry(e, 'Папка уже сущствует')

def create_save_dir(save_path):
    '''Создание директории для сохранения файлов'''
    print('fssf')
    try:
        if not path.exists(save_path):
                makedirs(save_path)
    except (FileNotFoundError, OSError) as e:
        log_entry(e, "Ошибка доступа к директории сохранения: " + 
                  save_path +
                  ". Измените SAVE_PATH в setting.ini")
        sys.exit()
    log_entry("Доступ к директории сохранения получен")
    return save_path


def create_dump_dir():
    dump_path = path.join(WORK_DIR, 'dump')
    if not path.exists(dump_path):
        makedirs(dump_path)
        log_entry('Создана директория сохранения предварительных файлов')
    return dump_path
    
def create_date (type_date):
    now = datetime.now()
    if type_date == '.':
        return str(now.strftime("%Y.%m.%d.%H.%M.%S"))
    if type_date == '-':
        return str(now.strftime("%Y-%m-%d_%H-%M-%S"))

def creat_name_files():
    '''Функция возвращает строку с текущей датой и именем компьютера'''
    date = create_date ('.')
    name_arm = "_ARM_" + node()
    return (date, name_arm)

def date_datafile():
    now = datetime.now()
    date_now = str(now.strftime("%Y%m%d_%H%M%S%f")[:19])
    return date_now

def create_ssn(date_record):
    name_arm = node()
    name = f"ssn_{date_datafile()}.dat"
    with open(f"{WORK_DIR}/dump/ssn_{date_datafile()}.dat", mode="w", encoding='utf-8') as ssn_file:
        # file_writer = csv.writer(ssn_file, delimiter = "|")
        # file_writer.writerow(["0", Ss_src, date_record, rec_length, 1, 1, 0, "", "", "", "", "", "", "", "", name_arm, "", "", "", "", "", "", "", "", "", "", arm_location, "", "", "", "", "", ""])
        ssn_file.write(f"0|{Ss_src}|{date_record}|{rec_length}|1|1|0|||||||||{name_arm}|||||||||||{arm_location}||||||")
        
    return name

def create_trf(name_mic_file, name_speak_file):
    name = f"traf_{date_datafile()}.dat"
    with open(f"{WORK_DIR}/dump/{name}", mode="w", encoding='utf-8', newline='') as ssn_file:
        ssn_file.write(f"0|0|audio/pcm_ik||0\\{name_mic_file}|UTF-8|2")
        ssn_file.write('\n')
        ssn_file.write(f"1|0|audio/pcm_ik||0\\{name_speak_file}|UTF-8|3")
 
    
    return name

def creat_file_contents(name_ssn, name_trf):
    now = datetime.now()
    date_now = str(now.strftime("%Y.%m.%d %H:%M:%S"))
    with open(f"{WORK_DIR}/dump/file.contents", mode="w", encoding='utf-8') as file_contents:
      file_contents.write(f"Sessions-File:{name_ssn}\n")
      file_contents.write(f"Traffic-File:{name_trf}\n")
      file_contents.write("Version:MNK.2.1\n")
      file_contents.write("Sessions-File-Rows:1\n")
      file_contents.write("Traffic-File-Rows:2\n")
      file_contents.write(f"Creation-Date:{date_now}")


def del_dump():
    dir = f'{WORK_DIR}/dump'
    if path.exists(dir):
        for files in listdir(dir):
            path_dir = path.join(dir, files)
            try:
                shutil.rmtree(path_dir)
            except OSError:
                remove(path_dir)
        

def create_ez():
    name_zip = f"{create_date('-')}_{node()}"
    directory = pathlib.Path(f"{WORK_DIR}/dump/")
    with ZipFile(f"{save_dir}/{name_zip}.ez", mode="w") as archive:
        for file_path in directory.rglob("*"):
            archive.write(
                file_path,
                arcname=file_path.relative_to(directory)
            )
    log_entry(f'ez {name_zip} сформирован')


if __name__ == '__main__':
    # create_dump_dir()
    # create_ssn('2023.05.02 15.27.04')
    # create_trf('asdfasld;fkmasdk', 'asdfasdfasdasd')
    # create_trf_dir()
    # creat_file_contents('asdnkcasdkjc', 'asdnklcsk', 'asdfnksd')
    # create_zipfile()
    # create_ez()
    # del_dump()
    pass
