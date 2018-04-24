#!/usr/bin/env python3

#Edited by Zach and Chris, 13APR18
import config #config file
import mysql.connector #database connector
from mysql.connector import errorcode #error for mysql
import hashlib, datetime, os, shelve, cgi, urllib.parse
from http import cookies
import cgitb
import time
import cookie #our own cookie.py
#created by Eatmon/Makkonen

cgitb.enable()

form = cgi.FieldStorage() # only needs to be instantiated once

try:
  '''cnx = mysql.connector.connect(user='theuser',
                                password = 'thepassword',
                                host = 'thehostserver',
                                database='thedatabase')'''
  cnx = mysql.connector.connect(user=config.USER,
                                password = config.PASSWORD,
                                host = config.HOST,
                                database=config.DATABASE)
				#connect to database using config.py parameters
				
#check for errors
except mysql.connector.Error as err:
  #print out errors for mysql connect failure
  print ( "Content-type: text/html" )
  print()
  print ("""\
  <!DOCTYPE html>
  <html>
  <head>
  <meta charset = "utf-8">
  <title>Message Board</title>
  <style type = "text/css">
  table, td, th {border:1px solid black}
  </style>
  </head>
  <body>
  """)
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err) #prints out exact error
  print("<p>Fix your code or Contact the system admin</p></body></html>")
  quit()
#create cursor to send queries
cursor = cnx.cursor()

"""

This function handled authentication of the session, 
through reading in the HTTP_COOKIE environment variable, 
parsing it for session ID, 
then checking to see if the server had a matching session file.  
It returned the session ID as well as whether a matching session could be found as a boolean expression.

"""
def sessionAuthenticate():
    cookie = cookies.SimpleCookie() #sets up cookie interface
    string_cookie = os.environ.get('HTTP_COOKIE') #gets cookie enviornment var
    issession = False 
    sid=0
    if not string_cookie:
       message = 'No cookie - no session'
       return(issession,sid)
    else:
       cookie.load(string_cookie) #loads in cookie
       if 'sid' in cookie: #if cookie has an sid parameter
         sid = cookie['sid'].value  #gets session id value from cookie 
         issession=True
         return(issession,sid) #returns session information
       else:
         message = '<p>No sid - no session </p>' #if cookie doesn't have sid parameter
         return(issession,sid) 
"""
This function generated the bulk of the message board HTML, 
listing user name, providing a logout button, as well as querying the Messages table, 
and printing each message with its time, poster, and a delete button.  
To determine whether a delete button should be presented for each individual message, the logged in username was compared to the message poster username.  
If they were the same, or the logged in user was an admin, a delete button would be created by the message.  
"""
def generateMessageBoard(uname,utype,sid):
    HTML = "<div class=\"divclass\">Username: "+uname+"</div><form action=\"./messageBoard.py\" method = \"post\" id=\"usrform3\"><input type=\"hidden\" name = logOut value =" + str(sid) + "><br><input name = \"Log out\" type=\"submit\" value = \"Log Out\"></form>"

    HTML += "<h2> Welcome To A Better Facebook </h2>"
    #parse database for stored messages from Messages table
    query = "SELECT * from Messages ORDER BY TDate ASC;"  #query to get all messages in chronological order
    cursor.execute(query) #executes query of entire Message table
    for (Username,Message,TDate,MessageID) in cursor:#goes through message table one by one
	#generates HTML for each message containing message, time, username
        HTML += "\n<div class=\"container\">"
        HTML += "\n<p><b>" + Username + "</b></p>"
        HTML += "\n<p>" + Message + "</p>"
        HTML += "\n<span clgass=\"time-right\">" + str(TDate) + "</span>"
        if Username == uname or utype == "admin": #checks permissions for ability to deleter
	#admins can delete all messages, normal users can delete their own messages
	#if logic supports deletion, generates HTML button for the message allowing for deletion of specified message, linked to the message/mySQL Messages table by MessageID parameter
            HTML += "<form action=\"./messageBoard.py\" method = \"post\" id=\"usrform2\"><input type=\"hidden\" name = strDel value =" + str(MessageID) + "><br><input name = \"delete\" type=\"submit\" value = \"Delete\"></form>"
        HTML += "\n</div>"

    return HTML #return full HTML string


"""
This function is utilized when the user clicks a delete button next to a message.  The messageID is utilized to create a SQL DELETE query for the specific message.  
Following deletion, the webpage is reloaded with a javascript statement, repopulating the table without the deleted message.
"""

def deleteMessage(): #this will conduct deletion of messages from SQL table and regenerate message board
    deleteButton = form.getvalue("delete") #checks for delete button press
    if deleteButton == "Delete": #if button pressed
        MessageID = form['strDel'].value #pulls messageID associated to delete button
        query = "DELETE FROM Messages WHERE MessageID = " + str(MessageID) + ";" 
	#forms SQL query to delete specified message
        cursor.execute(query,int(MessageID))
	#executes query, commits and closes connection to commit deletion
        cnx.commit()
        cnx.close()
        print('<script type="text/javascript">window.location.href = "./messageBoard.py";</script>')
	#reloads page to regenerate message board

"""
This is called when a user is logging out.  
Using the sid that is passed in, the script uses os.remove() to delete the server-side session file.  Additionally, the cookie is read in and set to 0 to delete. 
"""

def deleteCookie(sid): #deletes session cookie and session file
    cookie = cookies.SimpleCookie()
    string_cookie = os.environ.get('HTTP_COOKIE')
    session_file = '/tmp/sess_' + sid
    session = os.remove(session_file)    
    cookie['sid'] = 0
    print(cookie)
    return



"""
Creates text area form which is used to post a message
"""

def postMessage():#creates text area form which is used to post a message
    HTML = "<form action=\"./messageBoard.py\" method = \"post\" id=\"usrform\"><textarea name = \"message\" rows=\"4\" cols=\"50\"> </textarea><br><input name = \"insert\" type=\"submit\" value = \"Submit\"></form>"
    return(HTML)

"""
This function is utilized when a user clicks the submit button next to the textarea field that allows for message posting.  
It crafts a SQL INSERT query to insert the message, along with the current time and user posting.    
After execution, the page is reloaded with a javascript statement, allowing the message board to repopulate with the new message.
"""
def checkMessage(uname,sid): #on insert message button press, inserts message into table and reloads
    #get value for insert button and use if logic to confirm it was pressed	
    insertButton = form.getvalue("insert")
    if insertButton == "Submit":
        message = form['message'].value #actual string user enters in text area
        query = "INSERT INTO Messages (Username,Message,TDate) VALUES (%s,%s,%s);" 
	#forms query which inserts new message using username, string of message, and current time
        myTime = time.asctime( time.localtime(time.time())) #gets current local time
        cursor.execute(query,(uname,message,str(myTime))) #executes INSERT query with parameters
        print("Sucess") 
        cnx.commit() #commits change
        print('<script type="text/javascript">window.location.href = "messageBoard.py";</script>')
	#reload page

"""
This is the general function that handles the majority of the control flow for the script execution.  
It opens the shelve session file and pulls out useful fields for the other functions to utilize.  
It then generates some basic HTML for the page from the config.py file, and then executes local functions to allow for all page functionality to occur.
"""
def managerOfSession(sid):#manages/validates session and generates page HTML with other functions
    HTML = None
    defaultPageGen = 1
    try: #tries to open session id file to determine existing session
        with shelve.open('/tmp/sess_' + sid) as s:
            existing = s['key1']
        uname = existing['uname'] #pulls username, permissions variables from shelve file
        utype = existing['utype']
    except: #if no session ID found for user, delete user SID cookie if possible
		#then redirect to index 
        print(config.HEADER)
        print(config.BODY)
        print('<script type="text/javascript">window.location.href = "index.html";</script>')
        print(config.FOOTER)
    if defaultPageGen == 1:
        print(config.HEADER)
        print(config.BODY)
        print(generateMessageBoard(uname,utype,sid))
        print(postMessage())
        checkMessage(uname,sid)
        deleteMessage()
        logOut(sid)
        print(config.FOOTER)
"""
When the user clicks the logout button, it calls deleteCookie(sid) to ensure session deletion, 
and allows for javascript redirect to the index page for the user to log in again.
"""

def logOut(sid): #takes sid to handle logging out
  
    logOut = form.getvalue("Log out")
    if logOut == "Log Out":   
        deleteCookie(sid)
        print('<script type="text/javascript">window.location.href = "./index.html";</script>')
    pass

def main(): #calls session authentication if user is logged in, no login throws an error
    (issession,sid) = sessionAuthenticate()
    if sid != None:
        managerOfSession(sid)
    else:
        print("error")
main()
