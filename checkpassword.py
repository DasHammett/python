#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
from urllib.request import urlopen, Request
import re
import getpass

# Mask password input from user
password = getpass.getpass("Enter password: ")

# Generate SHA1 from password
hashedPassword = hashlib.sha1(str(password).encode("utf-8")).hexdigest()

# Get the first letters from the hash
hashedPasswordSmall = hashedPassword[0:5]

# Send the small hash to api and return list of hashes matches
urlAndParams = "https://api.pwnedpasswords.com/range/" + hashedPasswordSmall
req = Request(urlAndParams, headers = {"User-Agent":"Mozilla/5.0"}) # avoid getting Forbidden from website
response = urlopen(req).read()
response = response.decode("utf-8") # Necessary for further steps as object is byte, not str

# Remove newline literals
responseClean = re.sub('\r\n'," ",str(response))

# Create dictionary with hashes and number of times seen
responseDict = dict((k,int(v)) for k, v in (e.split(":") for e in responseClean.split(" ")))

# Iterate over the dictionary
findings = 0
for key, value in responseDict.items():
    if str(hashedPasswordSmall.upper()+key) == str(hashedPassword.upper()):
        print("Password found! " + str(key) + ": " + str(value) + " times")
        findings += 1
        break
if findings == 0:
    print("Password not found!")


