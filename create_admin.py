#!/usr/bin/env python

from getpass import getpass
from config import DB_PORT, DB_HOST, DB_NAME
from db import DBCommonData
from pymongo import MongoClient

if __name__ == "__main__":
    with MongoClient(host=DB_HOST, port=DB_PORT) as client:
        db = client[DB_NAME]
        data = DBCommonData(db)
        data.ensure_indices()

        username = raw_input("user name?")
        password = getpass("password?")
        password_verifier = getpass("password(input again)?")

        if password != password_verifier:
            print "Input passwords don't match"
        else:
            realname = raw_input("real name?")
            email = raw_input("email?")
            phone = raw_input("phone?")

            data.add_admin(username, password, realname, email, phone)
            print "DONE."
