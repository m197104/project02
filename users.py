import hashlib
# user class- adds, deletes, prints users
import mysql.connector
from mysql.connector import errorcode
import config
#created by laurel

class users:
      # This class is used to create and maintain user accounts

      def __init__(self):
        pass

      #add a user to the database
      #songID is AUTO_INCREMENT and votes has a default of 0, so no need to worry about them

#adds user to Users table by hashing password, ensures that user isn't already present in table
      def addUser(self, cursor, username, name, password):
        #Hash the Password
        success= False
        hash_object = hashlib.sha512(bytes(password, "utf-8"))
        hashPass = hash_object.hexdigest()
        #create query statement
        query = "INSERT INTO Users VALUES (%s, %s, %s, %s);"   # + user + "','" + password + "')"
        #execute the query
        try:
          cursor.execute(query, (username, name, hashPass, "regular"))
         # print ("<p> Executed statement: " + cursor.statement + "</p>")
          success = True
        except mysql.connector.Error as err:
          #for DEBUG only we'll print the error - we should print some generic message instead for production site
          print ('<p style = "color:red">')
          print ()
          print ('</p>')
        return success

#authenticates user by checking the Users table for existing user
#then compares entered and stored hashed passwords
      def authenticateUser(self, cursor, username, password):

          #####need to make work line below

          #query = "SELECT Password FROM Users WHERE Username = 'm197102';"    #gives hashed password in database
          query1 = "PREPARE chk FROM 'SELECT Password FROM Users WHERE Username=?' "
          cursor.execute(query1)

          query2 = "SET @l = '" +username + "'"
          cursor.execute(query2)
          #SET @p = "workharder";

          query = "EXECUTE chk USING @l;"
          cursor.execute(query)   #"SELECT Password FROM Users WHERE Username = %s", (username))
          tablepass = cursor.fetchone()
          #print(type(hashedpass))

          if (tablepass):
              hashedpass = str(tablepass[0])

              #query2 = "SELECT PASSWORD(%s) "
              hash_object = hashlib.sha512(bytes(password, "utf-8"))
              givenpass = hash_object.hexdigest()

              #givenpass = password

              if (givenpass == hashedpass):
                  return True
              else:
                  return False
          else:
              return False
