import serial

try:
    from serial.tools.list_ports import comports
except ImportError:
    print "comports not present, check serial library"
    comports = None


port = None

#prefijo para el puerto serial, reemplazar de acuardo al sistema
portpattern = "/dev/ttyACM"
puerto_serie = "/dev/ttyACM0"

def open_serial():
    if comports:
        for pname in comports():
            if(pname[0].find(portpattern) == 0):
                portname = pname[0]
    try:
        global port
        port = serial.Serial(puerto_serie, 9600)
        #port = serial.Serial(portname, 9600)
        print "conexion abierta en ", portname

    except Exception, error:
        print error


def generateFile():
    print "generating file"


def main():
    count = 0
    open_serial()
    port.write('a')
    command = None
    print "data written to port"
    try:
        while True:

            if not command:
                
                command = raw_input('Presione a para iniciar el bordado')

            if command == 'a':
                port.write(command)
            
            if port.inWaiting() > 0:
                data = port.read()               
                print "dato entrante: ", data
                
                if data == 'b':
                    print "Termino el proceso de bordado"
                    generateFile()
                    port.write('a')

    except KeyboardInterrupt:
            print "Terminando programa, cerrando puertos"
            port.flush()
            port.close()


if __name__ == '__main__':
    main()


