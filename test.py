import serial
import threading
import time
from gps import *
import gpsd
import queue

global log
log = queue.Queue(10)

def main():
    print("")

    #new_mod()

    test_q()
    #gpsdev = gps(device="/dev/ttyS0")

    #get_pos_data(gpsdev)

    #t = threading.Thread(group=None, target=reader)
    #t.start()


    #writer()





def test_q():
    global log
    counter = 0
    while not log.full():
        log.put("action {value}".format(value=counter))
        print("added action {value}".format(value=counter))
        counter = counter + 1
        time.sleep(1)
        if log.full():
            log.get()



def new_mod():
    gpsd.connect()
    packet = gpsd.get_current()
    print(packet.position())


def get_pos_data(gps):
    try:
        while 1:
            next = gps.next()
            print(next)
            if next['class'] == 'TPV':
                lat = getattr(next, 'lat', "Unknown")
                lon = getattr(next, 'lon', "Unknown")
                print("current pos: lon=" + str(lon) + " lat=" + str(lat))
            else:
                print("no translation possible")
                print(next)
                get_pos_data(gps)
    except KeyboardInterrupt:
        print("EXIT")
        exit(1)

def writer():
    while 1:
        ser = serial.Serial('/dev/ttyS0', 9600)
        print("writing data")
        ser.write(b'test\r')
        ser.close()
        time.sleep(1)

def reader():
    while 1:
        with serial.Serial('/dev/ttyS0', 9600) as ser:
            x = ser.readline()
            s = x.decode('utf-8')
            print(s)
            




if __name__ == "__main__":
    main()