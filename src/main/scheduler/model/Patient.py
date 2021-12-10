"""
* Kenny "Ackerson" Le
* 11/21/21
* CSE 414: HW6 — Vaccine Scheduler
* Description: Patient represents a patient user type and contains various
* functions and permissions for a user to interact with the Vaccine Scheduler.
* Patient is a child class of the User parent class and inherits all User functions.
"""

from src.main.scheduler.db.ConnectionManager import ConnectionManager
from src.main.scheduler.util.Util import *
from src.main.scheduler.model.User import *
import pymssql


class Patient(User):
    def get(self):
        """
        Retrieves and returns a patient's information from the database
        @return: a patient's information if it exists in the database, nothing otherwise
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_patient_details = "SELECT Salt, Hash FROM Patient WHERE Username = %s"
        try:
            cursor.execute(get_patient_details, self.username)
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
            print("Error occurred when getting Patients")
            cm.close_connection()
            return None
        cm.close_connection()
        return None

    def save_to_db(self):
        """
        Saves the user's information to the patient database
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        add_caregivers = "INSERT INTO Patient VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash_code))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Patient")
            sql_rc = str(db_err.args[0])
            print("Exception code: " + str(sql_rc))
        finally:
            cm.close_connection()
