"""
* Kenny "Ackerson" Le
* 11/18/21
* CSE 414: HW6 — Vaccine Scheduler
* Description: Caregiver represents a caregiver user type and contains various
* functions and permissions for a user to interact with the Vaccine Scheduler.
* Caregiver is a child class of the User parent class and inherits all User functions.
"""

from src.main.scheduler.db.ConnectionManager import ConnectionManager
from src.main.scheduler.util.Util import *
from src.main.scheduler.model.User import *
import pymssql


class Caregiver(User):
    def get(self):
        """
        Retrieves and returns a caregiver's information from the database
        @return: a caregiver's information if it exists in the database, nothing otherwise
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash_code = calculated_hash
                    return self
        except pymssql.Error:
            print("Error occurred when getting Caregivers")
            cm.close_connection()

        cm.close_connection()
        return None

    def save_to_db(self):
        """
        Saves the user's information to the caregiver database
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash_code))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Caregivers")
            sql_rc = str(db_err.args[0])
            print("Exception code: " + str(sql_rc))
        finally:
            cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):
        """
        Takes a date and uploads that as an availability to the Availabilities database
        @param d: datetime object formatted as YYYY-MM-DD
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = f"INSERT INTO Availabilities (Time, Username, Available) " \
                           f"VALUES ('{d}', '{self.username}', 1)"
        try:
            cursor.execute(add_availability)
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when updating caregiver availability")
            sql_rc = str(db_err.args[0])
            print("Exception code: " + str(sql_rc))
        finally:
            cm.close_connection()
