#!/usr/bin/env python3

#adapted from http://webpython.codepoint.net
#script to create or continue a session; time of last visit will be stored in a session variable

import hashlib, time, os, shelve
from http import cookies

import cgitb;
cgitb.enable()
"""
Creates cookie as well as session file
sid decided by hash of current time
session file loaded with parameters indicating user and permissions
"""
def makeCookie(username,utype):

    #try to read the 'sid' cookie
    cookie = cookies.SimpleCookie()
    string_cookie = os.environ.get('HTTP_COOKIE')

    if string_cookie == None:
       #create the 'sid' cookie if no cookies exist
       sid = hashlib.sha256(repr(time.time()).encode()).hexdigest() #hash of current time for
        #pseudorandom session id
       cookie['sid'] = sid #assigns session id variable
       message = 'New session'
    else:
       #try to read the 'sid' cookie (not just any cookie)
       cookie.load(string_cookie)
       if 'sid' in cookie:
         #read the 'sid'
         sid = cookie['sid'].value
       else:
         #create new sid ans store it in a cookie
         sid = hashlib.sha256(repr(time.time()).encode()).hexdigest()
         cookie['sid'] = sid
         message = 'New session'
    cookie['sid']['expires'] = 12 * 30 * 24 * 60 * 60 #sets expiration date

    #print the cookie to tell the browser to set it
    print (cookie)

   
    #open the session file (this also creates it if it does not exist)
    session_file = '/tmp/sess_' + sid
    session = shelve.open(session_file, writeback=True) #opens file
    session['key1'] = {
        'uname': username,
        'utype': utype
    } #saves username and usertype(perms) to session file

    session.close()

