#!/usr/bin/python

import pymysql
import time
import sys

#*** Connecting to DB ***
db = pymysql.connect(
    host = "localhost",
    user = "testuser",
    passwd = "test123",
    db = "SENSDB")

cursor = db.cursor()

#*** Incomming ***
try:
    trigger = input("Keyword is: ")
    if trigger == "Gjallerhorn":
        print ("welcome to the party")
        sql = "UPDATE noget SET TOILET = TOILET = 1"
        try:
            cursor.execute(sql)
            db.commit()
            time.sleep(1)
            print ("commit succes")
        except:
            db.rollback()
            db.close()
            print ("commit failure")

except KeyboardInterrupt:
    print ("Bye Bye !!")
