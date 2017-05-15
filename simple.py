import RPi.GPIO as GPIO
from lib_nrf24 import NRF24 #allows access to transceiver
import spidev               #SPI std. library
import time
import sys

def init_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def init_radio():
	pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]
    radio = NRF24(GPIO, spidev.SpiDev()) #create instance of radio, part of NRF24
    radio.begin(0, 17)          #begin radio, GPIO17=CSN pin
    radio.setPayloadSize(32)    #package size is 32 bytes 
    radio.setChannel(0x52)      #use channel 60, must match on both receiver and sender!

    radio.setDataRate (NRF24.BR_2MBPS) #communication speed, set to 2MBPS
    radio.setPALevel (NRF24.PA_MIN) #level set to min, higher level=longer dist=more power used
    radio.setAutoAck (True)     #auto send ack
    radio.enableDynamicPayloads() #enable dynamic payload size
    radio.enableAckPayload()      #send ack on payload

    radio.openReadingPipe(1, pipes[1])  #pipe for receiving data
    radio.printDetails()        #write all settings to screen

    radio.startListening()      #start listening for incoming payloads
    return (pipes, radio)

if __name__ == "__main__":
    
    init_GPIO()
    pipes, radio = init_radio()

    print ("Here we go!!! Press CTRL-C for clran exit")

    try:
		counter = 0
		while True:
			counter = (counter+1)%256
            akpl_buf = [c,1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8]
            pipe = []
            while not radio.available(pipe):
                time.sleep(1.0/1000.0)

            recv_buffer = []
            radio.read(recv_buffer, radio.getDynamicPayloadSize())
            print (recv_buffer)

            print ("Sending: %s"%akpl_buf)
            radio.writeAckPayload(1, akpl_buf, len(akpl_buf))
                        
    except KeyboardInterrupt:
        GPIO.cleanup()
        print ("Goodbye...")
