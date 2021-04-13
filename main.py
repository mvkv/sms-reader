import serial
import os
from serial.tools import list_ports
import time
import json
import logging
from uuid import uuid4

CHIP = "1A86:7523"
FILE_PATH = "sms.json"

logging.basicConfig(filename='logs.log', level=logging.DEBUG)

def saveSmsToFile(messages):
    with open(FILE_PATH, "w") as sms_file:
        try:
            data = json.load(sms_file)
        except json.JSONDecodeError as e:
            data = {}
        for msg in messages:
            data.update({str(uuid4()): msg})
        json.dump(data, sms_file)

def processMessages(raw_messages):
    logging.info(raw_messages)
    messages = []
    for msgIndex in range(len(raw_messages)):
        raw_message_decoded = raw_messages[msgIndex].strip().decode('utf-8').replace("\"", "")
        if "+CMGL" in raw_message_decoded:
            message = {}
            message_list = raw_message_decoded.split(",")
            message.update({
                "from": message_list[2],
                "date": message_list[4],
                "hour": message_list[5],
                "body": raw_messages[msgIndex + 1].strip().decode('utf-8').replace("\"", ""),
            })
            messages.append(message)
    return messages

def readMessages():
    port.flushInput()
    time.sleep(1)
    port.write(b'AT+CMGL="ALL",1\r\n')
    return port.readlines()

if __name__ == "__main__": 
    connecting_port = list(list_ports.grep(CHIP))[0][0]
    port = serial.Serial(connecting_port, baudrate=9600, timeout=1)

    if port.isOpen():
        print(port.name + ' is open...!!!')
    else:
        port.open()

    # To disable echo
    port.write(b'ATE0\r\n')  
    time.sleep(1)
    port.write(b'AT+CMGF=1\r\n')
    time.sleep(1)

    raw_msgs = readMessages()
    msgs = processMessages(raw_msgs)
    saveSmsToFile(msgs)
