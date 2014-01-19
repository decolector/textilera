#!/usr/bin/python

import sys
import os
import subprocess
import time
import logging
from shutil import copy
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
import serial

try:
    from serial.tools.list_ports import comports
except ImportError:
    print "comports not present, check serial library"
    comports = None

class MountDirHandler(FileSystemEventHandler):

    def __init__(self,  portname="/dev/ttyACM0", portpattern = None):
        #super(MountDirHandler, self).__init__()
        self.port_name = portname
        self.port_pattern = portpattern
        self.port = None

        self.data = None
        
        self.queue_dir = "data"
        self.src_file = ""
        self.out_dir = ""
        self.current_file = ""
        self.file_list = []
        self.generateFileList()

    def on_created(self, event):

        print("mounted filesystem: ", event.event_type, ", ", event.src_path)
        if os.path.isdir(event.src_path):
            self.openSerial()
            time.sleep(3)
            self.dirname = os.path.split(self.out_dir)[1]
            print("usb montada en: ", self.dirname)            
            self.out_dir = event.src_path

            #erase file from watched dir, but only files.
            for the_file in os.listdir(self.out_dir):
                file_path = os.path.join(self.out_dir, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception, e:
                    print e


            self.sendFile()
            self.removeFileFromQueue()
	    time.sleep(5)
            #unmount filesystem
            subprocess.call("umount /dev/sdb1",shell=True)
            print("desmontando usb")

            if self.port:
                print("sending command to serial")
                self.sendCommand("r")



    def on_deleted(self, event):
        print("usb desmontada ", event.event_type)


    def generateFileList(self):
        if not self.queue_dir:
            return False
            
        else:

            self.file_list = [ os.path.join(self.queue_dir, fname)  for fname in os.listdir(self.queue_dir)]
            print "file list: ", self.file_list
            if len(self.file_list) > 0:
                self.current_file = self.file_list[0]
                return True
            else:
                self.current_file = None
                return False


    def removeFileFromQueue(self):
        # TODO errase file from folder
        if self.current_file:
            print "removiendo archivo usado"
            os.remove(self.current_file)
            self.generateFileList()
        else:
            print "no hay archivo, intentando nada"


    def sendFile(self):
        if self.current_file:
            print "copiado archivo ", self.current_file, " a la maquina"
            copy(self.current_file, self.out_dir)
            #copyfile(self.current_file, self.out_dir)
            #self.port.write('a')
        else: 
            print "no hay archivo, intentando nada"

    def openSerial(self):
            if self.port_pattern:
                if comports:
                    for pname in comports():
                        if(pname[0].find(self.port_pattern) == 0):
                            self.port_name = pname[0]
                try:
                    self.port = serial.Serial(self.port_name, 9600)
                    #port = serial.Serial(portname, 9600)
                    print "conexion abierta en ", self.port_name

                except Exception, error:
                    print error

            elif not self.port_pattern and self.port_name:

                try:
                    self.port = serial.Serial(self.port_name, 9600)

                except Exception, err:
                    print "Error opening serial port"
                    print err

    def sendCommand(self, command):
        self.port.write(command)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = MountDirHandler(portname=sys.argv[2])
    observer = Observer()
    observer.schedule(event_handler, path=sys.argv[1], recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    
