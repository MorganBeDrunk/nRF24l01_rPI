#!/usr/bin/python

import pymysql
import time
import sys
import smtplib

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
sql = "UPDATE noget SET SOAP = SOAP - 1"
sqlFetch = "SELECT SOAP FROM noget"
press = 1.90
total_vol = 20

#*** Incomming ***
try:
    trigger = input("Keyword is: ")
    if trigger == "Gjallerhorn":
        print ("welcome to the party")
        total_vol = total_vol - press
        print (total_vol)
        if total_vol < 20:
            try:
                cursor.execute(sql)
                cursor.execute(sqlFetch)
                result = cursor.fetchall()
                for row in result:
                    SOAP = row[0]
                    print ("SOAP=%s" % (SOAP))
                    if SOAP < 45:
                        print ("You need to order some more soap mate! ")
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
                print ("commit failure")

except KeyboardInterrupt:
    print ("Bye Bye !!")
