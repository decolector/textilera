#!/usr/bin/python

#uso:
# sudo python 

import sys
import os
from subprocess import check_call, CalledProcessError
import time
import logging
from shutil import copy

#from watchdog.observers import Observer
#from watchdog.events import LoggingEventHandler
#from watchdog.events import FileSystemEventHandler

import os
import time
from pyudev import Context, Monitor, MonitorObserver

import serial

try:
    from serial.tools.list_ports import comports
except ImportError:
    print "comports not present, check serial library"
    comports = None
#!/usr/bin/python

def print_device_event(device):

    print('background event {0.action}: {0.device_path}'.format(device))
    #print(dir(device))
    prefix = "/media/cmart"
    label = device.get('ID_FS_LABEL')
    global out_dir
    global port
    global out_dir
    global device_node
    #out_dir = "/media/cmart/ANDREA_2013"
    #print("label: " + label)
    #out_dir = prefix + label
    #if device.action == 'add' and label == "ANDREA_2013":
    if device.action == 'add':
        device_node = device.device_node
        if device_node.rfind('1') == len(device_node) - 1:
            print "device intserted: ", device_node
            
            try:
                os.mkdir(out_dir)

            except OSError as exc:
                print(exc)

            try:
                check_call(["mount", device_node, out_dir])
                print("mount point created ")

            except CalledProcessError:
                print("Some error mounting node")


            #print "device ", label, " inserted"
            #out_dir = prefix + label
            if os.path.exists(out_dir):
                print "mountpoint ", out_dir, " exists"
                openSerial()
                time.sleep(3)
                dirname = os.path.split(out_dir)[1]
                print(dirname)

                #erase file from watched dir, but only files.
                for the_file in os.listdir(out_dir):
                    file_path = os.path.join(out_dir, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception, e:
                        print e


                sendFile()
                removeFileFromQueue()
                #unmount filesystem
                time.sleep(2)
                check_call(["umount", device_node])
                print("el puerto es: ", port)
                global port
                if port:
                    print("sending command to serial")
                    sendCommand("r")

                print("ahora puede remover la memoria usb")
            else:
                print("mountpoint not created")
                    

    elif device.action == "remove" and device.device_node == device_node:
        print("device ", label, " removed")
        #os.unlink(out_dir)
        check_call(["rm", "-r", out_dir])
        print("punto de montaje eliminado")

    

#   for key, value in device.iteritems():
#       print( key , ', ', value)

#   for child in device.children:
#       for key, value in child.iteritems():
#           print( key , ', ', value) 



def generateFileList():
    if not queue_dir:
        return False
        
    else:
        global file_list
        global current_file
        file_list = [ os.path.join(queue_dir, fname)  for fname in os.listdir(queue_dir)]
        print "file list: ", file_list
        if len(file_list) > 0:
            current_file = file_list[0]
            return True
        else:
            current_file = None
            return False


def removeFileFromQueue():
    # TODO errase file from folder
    if current_file:
        print "removiendo archivo usado"
        os.remove(current_file)
        generateFileList()
    else:
        print "no hay archivo, intentando nada"


def sendFile():
    global current_file
    global out_dir
    if current_file:
        print "copiado archivo ", current_file, " a ", out_dir
        copy(current_file, out_dir)
        #copyfile(current_file, out_dir)
        #port.write('a')
    else: 
        print "no hay archivo, intentando nada"

def openSerial():
    global port_name
    global port_pattern
    global port
    if port_pattern:
        if comports:
            for pname in comports():
                if(pname[0].find(port_pattern) == 0):
                    port_name = pname[0]
        try:
            port = serial.Serial(port_name, 9600)
            #port = serial.Serial(portname, 9600)
            print "conexion abierta en ", port_name

        except Exception, error:
            print error

    elif not port_pattern and port_name:

        try:
            port = serial.Serial(port_name, 9600)

        except Exception, err:
            print "Error opening serial port"
            print err

def sendCommand(command):
    port.write(command)

#port_name = "/dev/ttyACM0"
port_name = sys.argv[1]
port_pattern = ""
port = None
device_node = ""
data = None

queue_dir = "data"
src_file = ""
out_dir = sys.argv[2]
current_file = ""
file_list = []
generateFileList()

print("el puerto es: ", port_name)
print("out dir es: ", out_dir)

if __name__ == "__main__":

    context = Context()
    monitor = Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block')
    observer = MonitorObserver(monitor, callback=print_device_event, name='monitor-observer')
    observer.daemon
    observer.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()