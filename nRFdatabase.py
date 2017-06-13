#!/usr/bin/python

import pymysql
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev
import time
import sys
import smtplib

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

#*** mail setup ***
mail_user = 'flushandhandwash@gmail.com'
mail_pssword = '*#DatHandWash#'
to_add = 'seschram@gmail.com'
from_add = mail_user
subject = 'Python Test'
header = 'To: ' + to_add + '\n' + 'From: ' + from_add + '\n' + 'Subject: ' + subject
body = 'Jeg vil gerne bestille en hel masse sæbe'
mail_text = header + '\n\n' + body
server = smtplib.SMTP('smtp.gmail.com',587)

#*** Connecting to DB ***
db = pymysql.connect(
    host = "localhost",
    user = "testuser",
    passwd = "test123",
    db = "SENSDB")
cursor = db.cursor()

#*** variables ***
sql_toilet = "UPDATE noget SET TOILET = TOILET + 1"
sql_sink = "UPDATE noget SET SINK = SINK + 1"
sql_soap = "UPDATE noget SET SOAP = SOAP - 1"
sqlFetch = "SELECT SOAP FROM noget"
press = 1.90
total_vol = 1000

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
            total_vol = total_vol - press
            if total_vol < 20:
                try:
                    cursor.execute(sql_soap)
                    db.commit()
                    cursor.execute(sqlFetch)
                    result = cursor.fetchall()
                    for row in result:
                        SOAP = row[0]
                        print ("SOAP=%s" % (SOAP))
                        if SOAP < 45:
                            print (mail_text)

                            server.ehlo()
                            server.starttls()
                            server.login(mail_user, mail_pssword)
                            server.sendmail(from_add, to_add, mail_text.encode("utf8"))
                            server.close()
                            print ('Mail sent')
                except:
                    db.rollback()
                    db.close()
                    print ('Commit failure')

        radio.writeAckPayload(1, akpl_buf, len(akpl_buf))
    except KeyboardInterrupt:
        GPIO.cleanup()
        db.close()
        print ("Bye Bye !!")
