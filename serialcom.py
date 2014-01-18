#!/usr/bin/python

#uso:
# sudo python 

import sys
import os
import time
import logging
from threading import Thread
from subprocess import check_call, CalledProcessError
import serial
from shutil import copy

#from watchdog.observers import Observer
#from watchdog.events import LoggingEventHandler
#from watchdog.events import FileSystemEventHandler

from pyudev import Context, Monitor, MonitorObserver



try:
    from serial.tools.list_ports import comports
except ImportError:
    print "comports not present, check serial library"
    comports = None
#!/usr/bin/python


class SerialCom(Thread):

    def __init__(self, portpattern = None, portname="/dev/ttyUSB0", outdir = "/media/textilera", queuedir = "data"):
        Thread.__init__(self)
        #port_name = "/dev/ttyACM0"
        self.port_name = portname
        self.port_pattern = portpattern
        self.port = None
        self.device_node = None
        self.data = None
        #self.label = None
        self.queue_dir = queuedir
        #self.src_file = ""
        self.out_dir = outdir
        self.current_file = ""
        self.file_list = []
        self.generateFileList()


    def run(self):
        self.context = Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='block')
        self.observer = MonitorObserver(self.monitor, callback=self.print_device_event, name='monitor-observer')
        self.observer.daemon
        self.observer.start()
        self.observer.join()


    def print_device_event(self, device):

        print('background event {0.action}: {0.device_path}'.format(device))

        #self.label = device.get('ID_FS_LABEL')
        if device.action == 'add':
            self.device_node = device.device_node
            if self.device_node.rfind('1') == len(self.device_node) - 1:
                print "device intserted: ", self.device_node
                
                try:
                    os.mkdir(self.out_dir)

                except OSError as exc:
                    print(exc)

                try:
                    check_call(["mount", self.device_node, self.out_dir])
                    print("mount point created ")

                except CalledProcessError:
                    print("Some error mounting node")


                #print "device ", label, " inserted"
                #self.out_dir = prefix + label
                if os.path.exists(self.out_dir):
                    print "mountpoint ", self.out_dir, " exists"
                    self.openSerial()
                    time.sleep(3)
                    dirname = os.path.split(self.out_dir)[1]
                    print(dirname)

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
                    #unmount filesystem
                    time.sleep(2)
                    check_call(["umount", self.device_node])
                    print("el puerto es: ", self.port)
                    if self.port:
                        print("sending command to serial")
                        self.sendCommand("r")

                    print("ahora puede remover la memoria usb")
                else:
                    print("mountpoint not created")

        elif device.action == "remove" and device.device_node == self.device_node:
            print("usb extraida")
            check_call(["rm", "-r", self.out_dir])
            print("punto de montaje eliminado")
            self.port.close()

        

    #   for key, value in device.iteritems():
    #       print( key , ', ', value)

    #   for child in device.children:
    #       for key, value in child.iteritems():
    #           print( key , ', ', value) 



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
            print "copiado archivo ", self.current_file, " a ", self.out_dir
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


    def quit(self):
        self.observer.stop()
        self.port.close()



"""
if __name__ == "__main__":



    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
"""