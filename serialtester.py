import time
from serialcom import SerialCom

serial_com = SerialCom(portname="/dev/ttyACM0",  queuedir = "misc/data/",  mountpoint = "/media/cmart/textilera/", jefdir = "EmbF5/MyDesign/")
if __name__ == "__main__":
	serial_com.start()

	try:
		while True:
			time.sleep(0.1)
	except KeyboardInterrupt:
		print("saliendo del programa")
		serial_com.quit()
