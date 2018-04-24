#!/usr/bin/env python3

#created by laurel, tom on 13apr
import cgi,cgitb
cgitb.enable()
params=cgi.FieldStorage()
#connects to mysql
import html 
import mysql.connector
from mysql.connector import errorcode
from users import users
import config
import cookie

def main():
    try: #tries to connect to mysql database
        cnx = mysql.connector.connect(user=config.USER,
                                        password = config.PASSWORD,
                                        host = config.HOST,
                                        database=config.DATABASE)

    except mysql.connector.Error as err: #on connection error prints error description
        print ( "Content-type: text/html" )
        print()
        print ("""\
          <!DOCTYPE html>
          <html>
          <head>
          <meta charset = "utf-8">
          <title>DB connection with Python</title>
          <style type = "text/css">
          table, td, th {border:1px solid black}
          </style>
          </head>
          <body>
          """)
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("<p>Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("<p>Database does not exist")
        else:
            print(err)
            print("<p>Fix your code or Contact the system admin")
        print("</p></body></html>")
        quit()
    cursor = cnx.cursor()

    logon(cursor) #passes cursor to logon function for logging in
    cursor.close()   #commit the transaction
    cnx.commit()  #this is really important otherwise all changes lost
    #close connection
    cnx.close()
    quit()


#code to log on a USER
def logon(cursor):
    #security- use html escape
    username = params.getvalue("user") #gets username
    username = html.escape(username, True)
    password = params.getvalue("pass") #gets password
    password = html.escape(password, True)
    #call authenticaTeUser
	
    legit = users.authenticateUser(users, cursor, username, password) #checks for correct credentials

    if (legit):    #user is in database
        #generate a random session ID cookie that has a set expiration date
        query1 = "PREPARE chk FROM 'SELECT Role FROM Users WHERE Username=?' "
        cursor.execute(query1)

        query2 = "SET @l = '" +username + "'"
        cursor.execute(query2)
        #SET @p = "workharder";

        query = "EXECUTE chk USING @l;"
        cursor.execute(query)   #"SELECT Password FROM Users WHERE Username = %s", (username))
        tablepass = cursor.fetchone() #gets first result
        utype = str(tablepass[0]) #checks user type (admin or regular)
        cookie.makeCookie(username,utype) #creates cookie for user session
        print ( "Content-type: text/html" )
        print( "Status: 303 See Other" ) #redirects user to messageboard on login
        print( "Location: messageBoard.py" )
        print()
        print ("""\
          <!DOCTYPE html>
          <html>
          <head>
          <meta charset = "utf-8">
          <link rel = "stylesheet" type = "text/css" href= "messageBoard.css">
          <title>DB connection with Python</title>
          <style type = "text/css">
          table, td, th {border:1px solid black}
          </style>
          </head>
          <body>
          """)

    else:#not correct user/credentials
        print ( "Content-type: text/html" )
        print()
        print ("""\
          <!DOCTYPE html>
          <html>
          <head>
          <meta charset = "utf-8">
          <title>Invalid</title>
          <link rel = "stylesheet" type = "text/css" href= "messageBoard.css">
          <style type = "text/css">
          table, td, th {border:1px solid black}
          </style>
          </head>
          <body>
          """)
    #user is not in database
        print('<h2>Invalid login</h2>')
        print('<form method="post" action="./index.html"> <button type="submit">Try again?</button> </form>')
    print('</body></html>')




main()
