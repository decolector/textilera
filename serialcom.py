#!/usr/bin/python

import sys
import os
import time
import logging
from threading import Thread, Timer
from subprocess import check_call, CalledProcessError
import serial
from shutil import copy
from pyudev import Context, Monitor, MonitorObserver
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


try:
    from serial.tools.list_ports import comports
except ImportError:
    print "comports not present, check serial library"
    comports = None



class new_file_handler(FileSystemEventHandler):

    def __init__(self, callback):

        self.cb = callback

    def on_created(self, event):
        self.cb()


class SerialCom(Thread):

    def __init__(self, portpattern = None, portname="/dev/ttyUSB0",  queuedir = "data/",  mountpoint = "/media/textilera/", jefdir = "EmbF5/MyDesign/"):
        Thread.__init__(self)
        #port_name = "/dev/ttyACM0"
        self.request_count = 0
        self.port_name = portname
        self.port_pattern = portpattern
        self.port = None
        self.device_node = None
        self.data = None
        #self.label = None
        self.queue_dir = queuedir
        #self.src_file = ""
        self.mount_point = mountpoint
        self.jef_dir = jefdir
        self.out_dir = self.mount_point + self.jef_dir
        self.current_file = None
        self.file_list = []
        self.generateFileList()

        self.timer = None
        


        
    def run(self):
        self.context = Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='block')
        self.observer = MonitorObserver(self.monitor, callback=self.device_event, name='monitor-observer')
        self.observer.daemon = True

        self.file_created_event = new_file_handler(self.generateFileList)
        self.file_observer = Observer()
        self.file_observer.schedule(self.file_created_event, self.queue_dir)
        self.file_observer.daemon = True
        
        self.file_observer.start()
        self.observer.start()


    def new_file(self):

        print("nuevo archivo creado")
        self.generateFileList()

        if self.sendFile():
            #unmount filesystem
            time.sleep(3)
            self.unmount_dev()
            self.openSerial()
            time.sleep(3)
            #print("el puerto es: ", self.port)
            if self.port:
                print("enviando dato serial al microcontrolador")
                self.sendCommand("r")

            print "peticion finalizada \n ######################"

        else:
            print("intentando mas tarde")
            self.timer = Timer(5.0, self.new_file).start()



    def device_event(self, device):


        #print('background event {0.action}: {0.device_path}'.format(device))

        if device.action == 'add':
            self.device_node = device.device_node
            if self.device_node.rfind('1') == len(self.device_node) - 1:
                self.request_count = self.request_count + 1
                print "######################\n memoria insertada, peticion numero: ", self.request_count
                self.generateFileList()
                self.mount_dev()

                self.checkCreateDirs(self.out_dir)
                #erase file from watched dir, but only files.
                print("borrando archivos existentes en la memoria usb")

                for the_file in os.listdir(self.out_dir):
                    file_path = os.path.join(self.out_dir, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception, e:
                        print e


                if self.sendFile():
                    #unmount filesystem
                    time.sleep(3)
                    self.unmount_dev()
                    self.openSerial()
                    time.sleep(3)
                    #print("el puerto es: ", self.port)
                    if self.port:
                        print("enviando dato serial al microcontrolador")
                        self.sendCommand("r")

                    print "peticion finalizada \n ######################"
                else:
                    print("esperando a que haya un nuevo archivo")
                    self.timer = Timer(5.0, self.new_file).start()
                    #self.file_observer.start()
                    #self.file_observer.join()


        elif device.action == "remove" and device.device_node == self.device_node:
            print("la memoria usb ha sido expulsada")
            self.port.close()



    def mount_dev(self):
        print "memoria usb insertada: ", self.device_node
                
        try:
            os.mkdir(self.mount_point)

        except OSError as exc:
            print(exc)

        try:
            check_call(["mount", self.device_node, self.mount_point])
            print("punto de montaje creado")

        except CalledProcessError:
            print("Ocurrio un error montando la memoria")



    def unmount_dev(self):
        print "desmontando punto de montaje: ", self.device_node
                
        try:
            check_call(["umount", self.device_node])
        except OSError as exc:
            print(exc)

        try:
            check_call(["rm", "-r", self.mount_point])
            print("punto de montaje borrado")

        except CalledProcessError:
            print("Ocurrio un error eliminando punto de montaje")


    def generateFileList(self):

        result = False
        self.file_list = [ os.path.join(self.queue_dir, fname)  for fname in os.listdir(self.queue_dir)]
        print "lista de archivos: ", self.file_list
        if len(self.file_list) > 0:
            if not self.current_file:
                self.current_file = self.file_list[0]

            result = True
        else:
            self.current_file = None
            result =  False

        print("current file: ", self.current_file)
        return result


    def sendFile(self):
        if self.current_file:
            print "copiado archivo ", self.current_file, " a ", self.out_dir
            copy(self.current_file, self.out_dir)
            print "removiendo archivo usado"
            os.remove(self.current_file)
            self.current_file = None
            self.generateFileList()
            #self.current_file = self.file_list[0]
            return True
        else: 
            print "no hay archivo, no se copia nada a la memoria"
            return False



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

    def checkCreateDirs(self, dirname):
        try:
            if not os.path.exists(dirname):
                if os.path.isdir(dirname):

                    print dirname," ya existe"
                else:
                    print dirname , " no existe, creandolo"
                    os.makedirs(dirname)

        except OSError, err:
            print err


    def quit(self):
        
    
        if self.observer:
            print("parando el observador de eventos")
            self.observer.stop()
            #self.observer.join()

        if self.file_observer:
            print("parando el observador de archivos")
            self.file_observer.stop()
            #self.file_observer.join()

        if self.timer:
            print("parando el timer")
            self.timer.cancel()
        
        #self.port.close()

