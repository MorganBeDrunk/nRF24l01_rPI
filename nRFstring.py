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
radio.setPALevel (NRF24.PA_MIN) #level set to min, higher level=longer dist=more power used
radio.setAutoAck (True)     #auto send ack
radio.enableDynamicPayloads() #enable dynamic payload size
radio.enableAckPayload()      #send ack on payload

radio.openReadingPipe(1, [0xe7, 0xe7, 0xe7, 0xe7, 0xe7])  #pipe for receiving data
radio.printDetails()        #write all settings to screen

radio.startListening()      #start listening for incoming payloads

#*** business ***
try:
    while True:
        akpl_buf = [1]
        while not radio.available(0):
            time.sleep(1.0/1000.0)

        receivedMessage = []
        radio.read(receivedMessage, radio.getDynamicPayloadSize())
        print ("Received: {}".format (receivedMessage))

        string = ""
        for n in receivedMessage:
            if (n >=32 and n <=126):
                string += chr(n)
#        print (string)
        
        if string == 'DESTINY2':
            print (string)

        radio.writeAckPayload(1, akpl_buf, len(akpl_buf))
except KeyboardInterrupt:
    GPIO.cleanup()
    print ("!!Bye Bye!!")
