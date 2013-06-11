#/usr/bin/python

import time
from sms_reader import SmsReader

reader = SmsReader()
global messages

if __name__ == "__main__":
    while True:
        reader.update()
        if len(reader.new_sms) > 0:
            messages = reader.new_sms
            print messages
            reader.new_sms = []

        time.sleep(1)
