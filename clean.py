#!/usr/bin/python

import pymysql
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev
import time
import sys

def setupNRF():
    GPIO.setmode(GPIO.BCM)
    radio = NRF24(GPIO, spidev.SpiDev())
    radio.begin(0, 17)
    radio.setPayloadSize(32)
    radio.setChannel(0x52)
    radio.setDataRate(NRF24.BR_2MBPS)
    radio.setPALevel(NRF24.PA_MIN)
    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()
    radio.openReadingPipe(1, [0xe7, 0xe7, 0xe7, 0xe7, 0xe7])
    radio.printDetails()
    radio.startListening()

    return radio;

def setupDB():
    db = pymysql.connect(
        "localhost",
        "testuser",
        "test123",
        "SENSDB")
    cursor = db.cursor()

    return db, cursor;

def receive(radio):
    akpl_buf = [1]
    while not radio.available(0):
        time.sleep(1.0/1000.0)
    receiveMessage = []
    radio.read(receiveMessage, radio,getDynamicPayloadSize())
    print ("Received: {}".format (receivedMessage))

    return receivedMessage;

def translate (receivedMessage):
    string = ""
    for n in receivedMessage:
        if (n >= 32 and n <= 126):
            string += chr(n)

    return string;

def dbStuff (db, cursor, string):
    if string == 'DESTINY2':
        print (string)
    sql = "UPDATE noget SET TOILET = TOILET + 1"
    try:
        cursor.excecute(sql)
        db.commit()
        time.sleep(1)
        print("Succes")
    except:
        db.rollback()
        print("Failure")
    radio.writeAckPayload(1, akpl_buf, len(akpl_buf))
    return;

def dbClose(db):
    db.close()

if __name__ == "main":
    setupNRF()
    setupDB()

    while True:
        try:
            receive()
            translate()
            dbStuff()
        except KeyboardInterrupt:
            dbClose()
            GPIO.cleanup()
