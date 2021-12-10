"""
* Kenny "Ackerson" Le
* 11/21/21
* CSE 414: HW6 — Vaccine Scheduler
* Description: Util contains a number of supporting functions related to a user's password
"""

import hashlib
import os
from datetime import datetime


def generate_salt():
    """
    Generates a random 16 size byte as the salt for a user's account
    @return: A random 16 size byte
    """
    return os.urandom(16)


def generate_hash(password, salt):
    """
    Takes a user's password and salt and generates a hashcode with it
    @param password: the user's password
    @param salt: the user's salt
    @return: the user's hashcode
    """
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=16)
    return key


def check_password(password):
    """
    Checks if the password matches basic security features:
    1. Password is at least 8 characters in length
    2. At least 1 character is a lower case
    3. At least 1 character is an upper case
    4. Contains a special character from the list: "!", "@", "#", "?"
    @param password: a user's password
    @return: true if all security features are met, false otherwise
    """
    is_long = len(password) > 8
    is_upper = any(letter.isupper() for letter in password)
    is_lower = any(letter.islower() for letter in password)
    special_char = ["!", "@", "#", "?"]
    is_special = any(letter in special_char for letter in password)

    return is_long and is_upper and is_lower and is_special


def assert_password_error():
    """
    Prints password error with hints
    """
    print("Invalid password! Password must be at least 8 characters, contain an uppercase, "
          "a lowercase, and a special character (!, @, #, ?)")


def format_date(year, month, day):
    date_str = f"{year}-{month}-{day}"
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def main():
    # temp_password = "Abcdefgh8!"
    # temp_password2 = "password"
    # print(f"Is this password ({temp_password}) valid: {check_password(temp_password)}")
    # print(f"Is this password ({temp_password2}) valid: {check_password(temp_password2)}")
    # print(generate_hash(temp_password2, generate_salt()))
    #
    # if not check_password(temp_password2):
    #     print("Do I get here")
    #
    # test = ["StringOne", "StringTwo", "StringThree"]
    # print(f"Test: {test}")
    # test = [word.lower() for word in test]
    # print(f"Test after modification: {test}")

    test = "2021-12-25"
    test2 = datetime.strptime(test, "%Y-%m-%d").date()
    print(type(test2))
    print(test2)


if __name__ == '__main__':
    main()
