#!/usr/bin/env python3
#Edited by Laurel and Tom, 13APR18

import cgi,cgitb
cgitb.enable()
params=cgi.FieldStorage()
#connects to mysql

import html
import mysql.connector
from mysql.connector import errorcode
from users import users
import config


#called when a user submits the signup form in index.html.
#Connects to the SQL database. Creates a cursor. 
#Calls addUser() in users.py in order to add a user to the database.
#Gives a success or error page.
#Closes the database connection properly


def main():
    try:  #try to connect to database w/ config params
        cnx = mysql.connector.connect(user=config.USER,
                                        password =  config.PASSWORD,
                                        host = config.HOST,
                                        database=config.DATABASE)

     #error handling for mysql connection
    except mysql.connector.Error as err:
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


    #passes cursor for signup usage
    signup(cursor)
    cursor.close()   #commit the transaction
    cnx.commit()  #this is really important otherwise all changes lost
    #close connection
    cnx.close()
    quit()


#code for inserting a user
#insertButton = params.getvalue("Sign Up")



#If insert button pushed, uses the cursor to add the user to the Users table
#then either outputs a welcome message on success or an error message on failure
#with a button to redirect back to index.html for signup/signin

#if insert button was pushed
def signup(cursor):
    #
    print ( "Content-type: text/html" )
    print()
    print ("""\
      <!DOCTYPE html>
      <html>
      <head>
      <meta charset = "utf-8">
      <title>Sign up</title>
      <link rel="stylesheet" type="text/css" href="messageBoard.css">
      <style type = "text/css">
      table, td, th {border:1px solid black}
      </style>
      </head>
      <body>
     """)
    #user is not in database
    print('<h2>Result</h2>')


    username = params.getvalue("user")
    username = html.escape(username, True)
    name = params.getvalue("name")
    name = html.escape(name, True)
    password = params.getvalue("pass")
    password = html.escape(password, True)

   
    result = users.addUser(users, cursor, username, name, password)
    #print either a confirmation message or error message
    if result:
        print ('<h2>Welcome ' + str(name) + '!  Click below to go back and log in!</h2>')
    else:
        print ('<h2>There is already a user with this name!</h2>')
    #now need to clean up database cursor, etc
    print('<form method="post" action="./index.html"> <button type="submit">Go to signin</button> </form>')

    print("</body></html>")

main()
