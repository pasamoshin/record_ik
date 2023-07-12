from configparser import ConfigParser
import json
import socket
from platform import node

config = ConfigParser()
config.read("settings.ini")



HOST = config["network_settings"]["server_ip"]  # The server's hostname or IP address
PORT = int(config["network_settings"]["port"])
name_pc = node()





def send_message(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    massege = {'name_pc':name_pc,
               'program':'record_ik', 
                'massege': message}
    massege_json = json.dumps(massege, ensure_ascii=False).encode('utf-8')
    a=bytes(massege_json)
    sock.sendto(a, (HOST, PORT))


        

