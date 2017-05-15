#!/usr/bin/python

import pymysql
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24 #allows access to transceiver
import spidev               #SPI std. library
import time
import sys

#***Setup***
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

#***connecting to DB***
db = pymysql.connect(
        host = "localhost",
        user = "testuser",
        passwd = "test123",
        db = "SENSDB")

cursor = db.cursor()

radio = NRF24(GPIO, spidev.SpiDev()) #create instance of radio, part of NRF24
radio.begin(0, 17)          #begin radio, GPIO17=CSN pin
radio.setPayloadSize(32)    #package size is 32 bytes 
radio.setChannel(0x52)      #use channel 52, must match on both receiver and sender!

radio.setDataRate (NRF24.BR_2MBPS) #communication speed, set to 2MBPS
radio.setPALevel (NRF24.PA_MIN) #level set to min, higher level=longer dist=more power used
radio.setAutoAck (True)     #auto send ack
radio.enableDynamicPayloads() #enable dynamic payload size
radio.enableAckPayload()      #send ack on payload

radio.openReadingPipe(1, pipes[1])  #pipe for receiving data
radio.printDetails()        #write all settings to screen

radio.startListening()      #start listening for incoming payloads
print ("Here we go!!! Press CTRL-C for clran exit")

try: 
        while True:
                akpl_buf = [1]
 #               pipe = []
                while not radio.available(pipe):
                        time.sleep(1.0/1000.0)

                recv_buffer = []
                radio.read(recv_buffer, radio.getDynamicPayloadSize())
                print (recv_buffer)
                c = c + 1
                if (c&1) == 0:
                        radio.writeAckPayload(1, akpl_buf, len(akpl_buf))
                        sql = "UPDATE noget SET TOILET = TOILET + 1"
                        try:
                                cursor.execute(sql)
                                db.commit()
                                time.sleep(1)
                                print ("input_1 succesful")
                        except:
                                db.rollback()
                                db.close()
                                print ("input_1 failure, DB closed")

#                if inputPIN_2 == False:
#                        sql = "UPDATE noget SET SINK = SINK + 1"
#
#                        try:
#                                cursor.execute(sql)
#                                db.commit()
#                                time.sleep(0.3)
#                                print ("input_2 succesful")
#                        except:
#                                db.rollback()
#                                db.close()
#                                print ("input_2 failure, DB closed")
except KeyboardInterrupt:
        db.close()
        GPIO.cleanup()
        print ("Goodbye...")
