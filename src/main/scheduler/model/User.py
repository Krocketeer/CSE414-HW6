"""
* Kenny "Ackerson" Le
* 11/21/21
* CSE 414: HW6 — Vaccine Scheduler
* Description: User is the parent class for other user type classes
* that defines general functions that each user should have
"""

from src.main.scheduler.db.ConnectionManager import ConnectionManager
import pymssql


class User:
    def __init__(self, username, password=None, salt=None, hash_code=None):
        """
        Takes a username and creates an account
        @param username: the name of the account
        @param password: [OPTIONAL] the password to the account
        @param salt: [OPTIONAL] the salt assigned to the account
        @param hash_code: [OPTIONAL] the hash generated from the password and the salt
        """
        self.username = username
        self.password = password
        self.salt = salt
        self.hash_code = hash_code

    # getters
    def get(self):
        """
        Gets a users detail from the database
        """
        pass

    def get_username(self):
        """
        Gets the account's name
        @return: the account's username
        """
        return self.username

    def get_salt(self):
        """
        Gets the salt associated to the account
        @return: the account's salt
        """
        return self.salt

    def get_hash(self):
        """
        Gets the hash associated to the account
        @return: the account's hash
        """
        return self.hash_code

    def save_to_db(self):
        """
        Saves the user account to the database
        """
        pass
