#!/usr/bin/python

import os, time
import xml.etree.ElementTree as ET
from serialcom import SerialCom
from sms_reader import SmsReader
from qr2jef import Qr2jef

CONFIG_FILE="config/config.xml"

xml = ET.parse(CONFIG_FILE)

SERIAL_PORT = xml.find('serial_port').text
SERIAL_PORT_PATTERN = xml.find('serial_port_pattern').text
OUT_DIR = xml.find('out_dir').text
QUEUE_DIR = xml.find('queue_dir').text
BACKUP_DIR = xml.find('backup_dir').text
ADB_PATH = xml.find('adb_path').text
REMOTE_SMS_DB = xml.find('remote_sms_db').text
LOCAL_SMS_DB = xml.find('local_sms_db').text
MAX_STITCH_LENGTH = xml.find('max_stitch_length').text
UNIT_WIDTH = xml.find('unit_width').text
UNIT_HEIGHT = xml.find('unit_height').text
STEP = xml.find('step').text
INTERVAL = xml.find('interval').text



"""
print SERIAL_PORT
print SERIAL_PORT_PATTERN
print OUT_DIR
print QUEUE_DIR
print ADB_PATH
print REMOTE_SMS_DB
print LOCAL_SMS_DB
print MAX_STITCH_LENGTH
print UNIT_WIDTH
print UNIT_HEIGHT
print STEP

"""

def checkCreateDirs(dirname):
    try:
        if not os.path.exists(dirname):
            if os.path.isdir(dirname):

                print dirname," existe y es un directorio"
            else:
                print dirname , " no existe, creandolo"
                os.mkdir(dirname)

    except OSError, err:
        print err

def main():

    checkCreateDirs(LOCAL_SMS_DB)
    checkCreateDirs(QUEUE_DIR)
    #checkCreateDirs(OUT_DIR)
    checkCreateDirs(BACKUP_DIR)

    reader = SmsReader(adb_path=ADB_PATH, 
                        local_sms_db = LOCAL_SMS_DB,
                        remote_sms_db=REMOTE_SMS_DB
                        )
    qrgen = Qr2jef(max_stitch_length=MAX_STITCH_LENGTH,
        unit_width=UNIT_WIDTH, 
        unit_height=UNIT_HEIGHT,
        step=STEP,
        queue_dir=QUEUE_DIR,
        backup_dir = BACKUP_DIR,
        )
    serial_com = SerialCom(portname = SERIAL_PORT, 
        outdir = OUT_DIR,
        queuedir = QUEUE_DIR
        )

    serial_com.start()
    #wait some time while serial comm is set.
    try:
        while True:
            reader.update()
            if reader.new_sms > 0:
                print "nuevos mensajes"
                for message in reader.new_sms:
                    print message
                    qrgen.generate(message)
                reader.new_sms = []

            time.sleep(float(INTERVAL))

    except KeyboardInterrupt:
            serial_com.quit()
            reader.quit()



if __name__ == '__main__':
    main()
