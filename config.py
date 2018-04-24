#!/usr/bin/env python3

USER = 'm197104'
PASSWORD = '234552lw'
HOST = 'midn.cyber.usna.edu'
DATABASE = 'm197104'

HEADER = "Content-type: text/html; charset=UTF-8; X-XSS-Protection: 1; Content-Security-Policy-Report-Only: : "

BODY =  """
<!DOCTYPE html>
<body>
<head>
<meta charset = "utf-8">
<title>Message Board</title>
<link rel = "stylesheet" type = "text/css" href= "messageBoard.css">
<style>
</style>
</head>
<body>
"""

display = """



"""
#basic HTML footer
FOOTER = """
</body>
</html>
"""
