import RPi.GPIO as GPIO      
from lib_nrf24 import NRF24 #allows access to transceiver
import time
import spidev               #SPI std. library

GPIO.setmode(GPIO.BCM)      #use GPIO number not pin numbers

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(GPIO, spidev.SpiDev()) #create instance of radio, part of NRF24
radio.begin(0, 17)          #begin radio, GPIO17=CSN pin
radio.setPayloadSize(32)    #package size is 32 bytes 
radio.setChannel(0x52)      #use channel 60, must match on both receiver and sender!

radio.setDataRate (NRF24.BR_2MBPS) #communication speed, set to 2MBPS
radio.setPALevel (NRF24.PA_HIGH) #level set to min, higher level=longer dist=more power used
radio.setAutoAck (True)     #auto send ack
radio.enableDynamicPayloads() #enable dynamic payload size
radio.enableAckPayload()      #send ack on payload

radio.openReadingPipe(1, pipes[1])  #pipe for receiving data
radio.printDetails()        #write all settings to screen

radio.startListening()      #start listening for incoming payloads
try:
    while True:
        ackPL = [1]
        while not radio.available(0):   #sleep when nothing is received
            time.sleep(1.0/1000.0)

        receivedMessage = []    #array to hold the received payload
        radio.read(receivedMessage, radio.getDynamicPayloadSize()) #populate array with received payload
        print ("Received: {}".format (receivedMessage)) #print the raw message to screen

        print("Translating received Message to unicode characters...")
        string = ""
        for n in receivedMessage:
            #decode into standard unicode set
            if (n >=32 and n <=126):
                string += chr(n)
        print (string)

        radio.writeAckPayload(1, ackPL, len(ackPL))
        print ("Loaded payload reply of {}".format (ackPL))
except KeyboardInterrupt:
    GPIO.cleanup()
    











    
