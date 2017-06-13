#!/usr/bin/python

import pymysql
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev
import time
import sys

#*** Setup ***
GPIO.setmode(GPIO.BCM)
radio = NRF24(GPIO, spidev.SpiDev()) #create instance of radio, part of NRF24
radio.begin(0, 17)          #begin radio, GPIO17=CSN pin
radio.setPayloadSize(32)    #package size is 32 bytes
radio.setChannel(0x52)      #use channel 60, must match on both receiver and sender!

radio.setDataRate (NRF24.BR_2MBPS) #communication speed, set to 2MBPS
radio.setPALevel (NRF24.PA_HIGH) #level set to min, higher level=longer dist=more power used
radio.setAutoAck (True)     #auto send ack
radio.enableDynamicPayloads() #enable dynamic payload size
radio.enableAckPayload()      #send ack on payload

radio.openReadingPipe(1, [0xe7, 0xe7, 0xe7, 0xe7, 0xe7])  #pipe for receiving data
radio.printDetails()        #write all settings to screen

radio.startListening()      #start listening for incoming payloads

#*** Connecting to DB ***
db = pymysql.connect(
    host = "localhost",
    user = "testuser",
    passwd = "test123",
    db = "SENSDB")

cursor = db.cursor()
sql_toilet = "UPDATE NOGET SET TOILET = TOILET + 1"
sql_sink = "UPDATE NOGET SET SINK = SINK + 1"
sql_soap = "UPDATE NOGET SET SOAP = SOAP + 1"
#*** Incomming ***
while True:
    try:
        akpl_buf = [1]
		
        while not radio.available(0):
            time.sleep(1.0/1000.0)

        receivedMessage = []
        radio.read(receivedMessage, radio.getDynamicPayloadSize())
        print ("Received: {}".format (receivedMessage))
        
        string = ""
        for n in receivedMessage:
            if (n >= 32 and n <= 126):
                string += chr(n)

#*** Business ***
        if string == 'A':
            print (string)
            try:
                cursor.execute(sql_toilet)
                db.commit()
                print ("Succes")
            except:
                db.rollback()
                print ("Failure")

        elif string == 'B':
            print (string)
            try:
                cursor.execute(sql_sink)
                db.commit()
                print ("Succes")
            except:
                db.rollback()
                print ("Failure")

        elif string == 'C':
            print (string)
            try:
                cursor.execute(sql_soap)
                db.commit()
                print ("Succes")
            except:
                db.rollback()
                print ("Failure")

        radio.writeAckPayload(1, akpl_buf, len(akpl_buf))
   
    except KeyboardInterrupt:
        GPIO.cleanup()
        db.close()
        print ("Bye Bye !!")

