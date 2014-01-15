#/usr/bin/python

#!/usr/bin/python

#programa de prueba para el control
#de la maquina de bordado

import sys
import os
import time
import subprocess
import serial
import logging
#from shutil import copyfile
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
from shutil import copy


try:
    from serial.tools.list_ports import comports
except ImportError:
    print "comports not present, check serial library"
    comports = None



class SerialCom(FileSystemEventHandler):

    def __init__(self, portpattern = None, portname="/dev/ttyACM0", queue_dir = None, out_dir="out/"):
        #prefijo para el puerto serie
        self.port_pattern = portpattern
        #nombre del puerto serie
        self.queue_dir = queue_dir
        self.mnt_dir = ""
        self.out_dir = out_dir

        if not os.path.exists(out_dir):
        	os.mkdir(out_dir)
        self.port_name = portname
        self.port = None
        #self.openSerial()
        self.data = None
        self.file_list = []
        self.generateFileList()
        time.sleep(3)
        if self.port:
            print "send first file"
            self.sendFile()
        

    def on_created(self, event):
        print("mounted filesystem: ", event.event_type, ", ", event.src_path)
        self.mnt_dir = event.src_path
        if os.path.isdir(event.src_path):
            self.openSerial()
            time.sleep(3)

            #si hay archivos para enviar
            
            if self.generateFileList():
           
                self.dirname = os.path.split(self.out_dir)[1]
                print(self.dirname)            
                #self.out_dir = event.src_path

                #erase file from watched dir, but only files.
                for the_file in os.listdir(self.mnt_dir):
                    file_path = os.path.join(self.mnt_dir, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception, e:
                        print e

                self.sendFile()
                self.removeFileFromQueue()
                #unmount filesystem
                subprocess.call("umount /dev/sdc1",shell=True)

                if self.port:
                    print("sending command to serial")
                    self.sendCommand("r")

            else:
                print "no hay archivos de entrada, intentando nada"




            self.sendFile()
            self.removeFileFromQueue()
            #unmount filesystem
            subprocess.call("umount /dev/sdc1",shell=True)

            if self.port:
                print("sending command to serial")
                self.sendCommand("r")
      


    def on_deleted(self, event):
        print("deleted filesystem: ", event.event_type)


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

    def sendCommand(self, command):
        self.port.write(command)


    def check(self):
    	if self.generateFileList():
            try:
                self.sendCommand('a')
                if self.port.inWaiting() > 0:
                    self.data = self.port.read()
                    if self.data == 'b':
                        print "bordado iniciado"
                        self.removeFileFromQueue()
                        self.data = None

                    elif self.data == 'c':
	                	print "Maquina ocupada, intentando mas adelante"
	                	self.data = None

                    else:
		             	print "dato serial desconocido"


            except Exception, err:
	            print "Error leyendo serial"
	            print err
	            pass
	            #self.port.close()
        else:
            print "no hay archivos de entrada, intentando nada"

    def quit(self):
        print "Cerrando puerto serial"
        self.port.flushOutput()
        self.port.close()
        #self.ev.set()
