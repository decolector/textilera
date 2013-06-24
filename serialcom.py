#/usr/bin/python

#!/usr/bin/python

#programa de prueba para el control
#de la maquina de bordado

import sys
import os
import time
from shutil import copyfile
import serial

try:
    from serial.tools.list_ports import comports
except ImportError:
    print "comports not present, check serial library"
    comports = None



class SerialCom:

    def __init__(self, portpattern = None, portname="/dev/ttyACM0", queue_dir = None, out_dir="out/"):
        #prefijo para el puerto serie
        self.port_pattern = portpattern
        #nombre del puerto serie
        self.queue_dir = queue_dir
        self.out_dir = out_dir

        if not os.path.exists(out_dir):
        	os.mkdir(out_dir)
        self.port_name = portname
        self.port = None
        self.openSerial()
        self.data = None
        self.file_list = []
        self.generateFileList()
        time.sleep(3)
        if self.port:
            print "send first file"
            self.sendFile()
        

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
            copyfile(self.current_file, self.out_dir)
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
                        print "birdado iniciado"
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
