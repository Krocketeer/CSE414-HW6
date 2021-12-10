"""
* Kenny "Ackerson" Le
* 11/18/21
* CSE 414: HW6 — Vaccine Scheduler
* Description: Scheduler runs the vaccine scheduling system between patients and caregivers by
* allowing users to create a new account and manage/reserve appointments for vaccines
"""

from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import generate_salt, generate_hash, check_password, \
    assert_password_error, format_date
from util.Error import DatabaseSaveError, DatabaseRetrievalError, DatabaseUpdateError
from db.ConnectionManager import ConnectionManager
from tabulate import tabulate
import pymssql
import random

# Global Objects to track current logged in patient and caregiver
# Note: It's always true that at most one of the CURRENT_CAREGIVER and CURRENT_PATIENT
#       is not null since only one user can be logged in at a time
CURRENT_PATIENT = None
CURRENT_CAREGIVER = None


def create_patient(tokens):
    """
    Creates a new patient with the command 'create_patient <username> <password>'
    @param tokens: Expression to run function
    * Token[0] = create_patient
    * Token[1] = <username>
    * Token[2] = <password>
    """

    # Check 1: the length for tokens need to be exactly 3 to include all information
    if len(tokens) != 3:
        print("Please try again making sure you have three arguments: "
              "'create_patient <username> <password>'")
        return None

    username = tokens[1]
    password = tokens[2]

    # Check if password meets required security specifications
    # False if doesn't meet, true if does
    if not check_password(password):
        assert_password_error()
        return None

    # Check if username currently exists in database
    if username_exists(username, "Patient"):
        print("Username taken, try again!")
        return None

    salt = generate_salt()
    hash_code = generate_hash(password, salt)

    # create the patient
    try:
        patient = Patient(username, salt=salt, hash_code=hash_code)
        # save to caregiver information to our database
        try:
            patient.save_to_db()
        except DatabaseSaveError:
            print("Create failed, Cannot save")
            return None
        print(" *** Account created successfully *** ")
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Create failed")
        return None


def create_caregiver(tokens):
    """
    Creates a new caregiver with the command 'create_caregiver <username> <password>'
    @param tokens: Expression to run function
    * Token[0] = create_caregiver
    * Token[1] = <username>
    * Token[2] = <password>
    """

    # Check if correct command is given
    if len(tokens) != 3:
        print("Please try again making sure you have three arguments: "
              "'create_caregiver <username> <password>'")
        return None

    username = tokens[1]
    password = tokens[2]

    # Check if password meets required security specifications
    # False if doesn't meet, true if does
    if not check_password(password):
        assert_password_error()
        return None

    # Check: check if the username has been taken already
    if username_exists(username, "Caregivers"):
        print("Username taken, try again!")
        return None

    salt = generate_salt()
    hash_code = generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash_code=hash_code)
        # save to caregiver information to our database
        try:
            caregiver.save_to_db()
        except DatabaseSaveError:
            print("Create failed, Cannot save")
            return None
        print(" *** Account created successfully *** ")
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Create failed")
        return None


def username_exists(username, user_type):
    """
    Takes a username and a user_type to check if the user exists in the corresponding database
    @param username: the name of the user
    @param user_type: the type of user (Caregiver or Patient)
    @return: False if the user does not exist i n the database, true otherwise
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    select_username = f"SELECT * FROM {user_type} WHERE Username = %s"
    try:
        cursor.execute(select_username, username)

        #  returns false if the cursor is not before the first
        #  record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when checking username")
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    Allows the client to log in as a patient
    @param tokens: Expression to run function
    * Token[0] = login_patient
    * Token[1] = <username>
    * Token[2] = <password>
    """

    global CURRENT_PATIENT
    if CURRENT_PATIENT is not None or CURRENT_CAREGIVER is not None:
        print("A user is already logged in! Please log out before logging into a different account")
        return None

    if len(tokens) != 3:
        print("Please try again making sure you have three arguments: "
              "'login_patient <username> <password>'")
        return None

    username = tokens[1]
    password = tokens[2]

    # Check if password meets required security specifications
    # False if doesn't meet, true if does
    if not check_password(password):
        assert_password_error()
        return None

    patient = None
    try:
        try:
            patient = Patient(username, password=password).get()
        except DatabaseRetrievalError:
            print("Error occurred when retrieving patient data. Please try again")
            return None
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when logging in. Please try again.")

    if patient is None:
        print("Error occurred. Please try again!")
        return None
    else:
        print(f"Patient logged in as: {username}")
        CURRENT_PATIENT = patient.username


def login_caregiver(tokens):
    """
    Allows the client to log in as a caregiver
    @param tokens: Expression to run function
    * Token[0] = login_caregiver
    * Token[1] = <username>
    * Token[2] = <password>
    """

    # check 1: if someone's already logged-in, they need to log out first
    global CURRENT_CAREGIVER
    if CURRENT_CAREGIVER is not None or CURRENT_PATIENT is not None:
        print("A user is already logged in! Please log out before logging into a different account")
        return None

    # Check 2: the length for tokens need to be exactly 3 to
    # include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again making sure you have three arguments: "
              "'login_caregiver <username> <password>'")
        return None

    username = tokens[1]
    password = tokens[2]

    # Check if password meets required security specifications
    # False if doesn't meet, true if does
    if not check_password(password):
        assert_password_error()
        return None

    caregiver = None
    try:
        try:
            caregiver = Caregiver(username, password=password).get()
        except DatabaseRetrievalError:
            print("Get Failed")
            return
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when logging in")

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
        return None
    else:
        print("Caregiver logged in as: " + username)
        CURRENT_CAREGIVER = caregiver.username


def search_caregiver_schedule(tokens):
    """
    Takes the appropriate function and prints all the caregivers are available on
    that day as well as the name and number of doses left for each vaccine
    @param tokens: Expression to run function
    * Token[0]: search_caregiver_schedule
    * Token[1]: <date> formatted in YYYY-MM-DD
    """

    if CURRENT_PATIENT is None and CURRENT_CAREGIVER is None:
        print("Please log in before searching for caregiver schedule")
        return None

    if len(tokens) != 2:
        print("Please try again making sure you have two arguments: "
              "'search_caregiver_schedule <date (YYYY-MM-DD)>'")
        return None

    date = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    get_caregivers = f"SELECT DISTINCT Username FROM Availabilities as A " \
                     f"WHERE '{date}' = A.Time AND 1 = A.Available"
    try:
        try:
            cursor.execute(get_caregivers)
        except DatabaseRetrievalError:
            print("Failed to print caregiver schedule. Please try again.")
            return None

        caregivers = list()
        for row in cursor:
            caregivers.append([row["Username"]])

        if not caregivers:
            print(f"No caregivers are available on {date}")
        else:
            print(f"Caregivers Available on {date}:")
            print(f'{tabulate(caregivers, headers=["Caregiver"])}\n')

    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when retrieving caregiver schedule")
        return None

    if caregivers:
        get_vaccines = f"SELECT * FROM Vaccines WHERE Doses > 0"
        try:
            try:
                cursor.execute(get_vaccines)
            except DatabaseRetrievalError:
                print("Failed to print vaccine availability. Please try again.")
                return None

            vaccines = list()
            for row in cursor:
                vaccines.append([row["Name"], row["Doses"]])
            print(f"Vaccine Availability:")
            print(f'{tabulate(vaccines, headers=["Vaccine Name", "Doses Remaining"])}\n')

        except pymssql.Error as db_err:
            sql_rc = str(db_err.args[0])
            print("Exception code: " + str(sql_rc))
            print("Error occurred when retrieving vaccine numbers")
    cm.close_connection()


def reserve(tokens):
    """
    Allows a user to reserve an appointment for a vaccine if there are remaining doses available
    for that vaccine and if there is a caregiver available on the selected date. If multiple
    caregivers are available on the date, a random caregiver is assigned to the appointment.
    @param tokens: Expression to run function
    * Token[0]: reserve
    * Token[1]: <date> formatted in YYYY-MM-DD
    * Token[2]: vaccine name
    """
    if CURRENT_PATIENT is None:
        print("Please log in as a patient before scheduling an appointment.")
        return None

    if len(tokens) != 3:
        print("Please try again making sure you have three arguments: 'reserve <date> <vaccine>'")
        return None

    date = tokens[1]
    vaccine = tokens[2].lower()
    if vaccine == "johnson & johnson" or vaccine == "johnson and johnson":
        vaccine = "Johnson & Johnson"
    else:
        vaccine = vaccine.capitalize()

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    # Get list of caregivers available on selected date
    caregivers = list()
    get_caregivers = f"SELECT DISTINCT Username FROM Availabilities as A " \
                     f"WHERE '{date}' = A.Time AND 1 = A.Available"
    try:
        try:
            cursor.execute(get_caregivers)
        except DatabaseRetrievalError:
            print("Failed to retrieve caregiver schedule. Please try again.")

        for row in cursor:
            caregivers.append(row["Username"])
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when retrieving caregiver schedule")
        return None

    # Check if there are no caregivers available on selected date
    if caregivers is not None:
        selected_caregiver = random.choice(caregivers)
    else:
        print(f"There are no appointment slots available on {date}. Please select another date"
              f"and try again.")
        return None

    # Get number of doses available for vaccine
    get_vaccine_num = f"SELECT Doses FROM Vaccines WHERE Name='{vaccine}'"
    doses_available = -1
    try:
        try:
            cursor.execute(get_vaccine_num)
        except DatabaseRetrievalError:
            print(f"Failed to get number of doses for the {vaccine} vaccine. Please try again.")
            return None
        for row in cursor:
            doses_available = row["Doses"]
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when retrieving vaccine availability")
        return None

    # Check if there are available doses for selected vaccine
    if doses_available < 1:
        print(f"Unable to book appointment for {vaccine} vaccine. "
              f"There are no more doses remaining.")
        return None

    get_num_appointments = "SELECT COUNT(*) as count FROM Appointment"
    num_appointments = None
    try:
        try:
            cursor.execute(get_num_appointments)
        except DatabaseRetrievalError:
            print("Unable to get appointment ID. Please try again.")
            return None

        for row in cursor:
            num_appointments = row["count"]

        if num_appointments is None:
            appointment_id = 1
        else:
            appointment_id = num_appointments + 1
        print(num_appointments)
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when creating details for appointment.")
        return None

    # Booking appointment
    book_appointment = f"INSERT INTO Appointment (ID, Time, Caregiver, Patient, Vaccine) " \
                       f"VALUES ({appointment_id}, '{date}', '{selected_caregiver}', " \
                       f"'{CURRENT_PATIENT}', '{vaccine}')"

    try:
        try:
            cursor.execute(book_appointment)
            conn.commit()
        except DatabaseUpdateError:
            print("Unable to update book appointment. Please try again.")
            return None

        print("Your appointment is now booked! The details are below:")
        print(tabulate([[appointment_id, date, selected_caregiver, CURRENT_PATIENT, vaccine]],
                       headers=["Appointment ID", "Date", "Caregiver", "Patient", "Vaccine"]))
        print("\n")

    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when booking appointment. Please make sure that you are selecting"
              " a date (YYYY-MM-DD) for which a caregiver is available and a vaccine that has"
              " doses available.")
        cm.close_connection()
        return None

    # Update availability of caregiver on date to 0 (unavailable)
    update_caregiver_availability = f"UPDATE Availabilities SET Available=0 WHERE" \
                                    f" Username='{selected_caregiver}' AND Time = '{date}'"
    try:
        try:
            cursor.execute(update_caregiver_availability)
            conn.commit()
        except DatabaseUpdateError:
            print("Unable to update caregiver availability. Please try again.")
            return None
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when updating caregiver availability")
        return None

    # Update Vaccine dosage
    update_vaccine_dose = f"UPDATE Vaccines SET Doses={doses_available - 1} WHERE Name='{vaccine}'"
    try:
        try:
            cursor.execute(update_vaccine_dose)
            conn.commit()
        except DatabaseUpdateError:
            print("Unable to update vaccine dosage availability. Please try again.")
            return None
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when updating vaccine dose amounts.")
        return None

    # print("- - - - - - - - - - - - - - - - - - - - - - -")
    # print(f"Appointment ID: {appointment_id}")
    # print(f"date: {date}")
    # print(f"Caregiver: {selected_caregiver}")
    # print(f"Patient: {CURRENT_PATIENT}")
    # print(f"Vaccine: {vaccine}")
    # print("- - - - - - - - - - - - - - - - - - - - - - -")

    cm.close_connection()


def upload_availability(tokens):
    """
    Allows caregivers to upload dates when they are available (have no appointments)
    @param tokens: Expression to run function
    * Token[0]: upload_availability
    * Token[1]: <date> formatted in YYYY-MM-DD
    """

    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global CURRENT_CAREGIVER
    if CURRENT_CAREGIVER is None:
        print("Please login as a caregiver first!")
        return None

    # check 2: the length for tokens need to be exactly 2
    # to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again making sure you have two arguments:"
              " 'upload_availability <date (YYYY-MM-DD)>'")
        return None

    date = tokens[1]
    # assume input is hyphenated in the format YYYY-MM-DD
    date_tokens = date.split("-")
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    year = int(date_tokens[0])
    d = format_date(year, month, day)
    try:
        try:
            caregiver = Caregiver(CURRENT_CAREGIVER)
            caregiver.upload_availability(d)
        except DatabaseUpdateError:
            print("Upload Availability Failed")
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when uploading availability")


def cancel(tokens):
    """
    Allows a user to cancel an appointment
    @param tokens: Expression to run function
    * Token[0]: cancel
    * Token[1]: <appointment_id>
    """

    if len(tokens) != 2:
        print("Invalid input! Please try again making sure you have two arguments: "
              "'cancel <appointment_id>'")
        return None

    appt_id = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        # Get appointment date, caregiver, and patient information
        get_appointment_details = f"SELECT Time, Caregiver, Patient, Vaccine FROM" \
                                  f" Appointment WHERE ID={appt_id}"
        try:
            cursor.execute(get_appointment_details)
        except DatabaseRetrievalError:
            print("Failed to retrieve appointment details. Please try again.")

        appointment = dict()
        for row in cursor:
            appointment["patient"] = row["Patient"]
            appointment["caregiver"] = row["Caregiver"]
            appointment["time"] = row["Time"]
            appointment["vaccine"] = row["Vaccine"]

        # Check if no user is currently logged in
        if CURRENT_PATIENT is None and CURRENT_CAREGIVER is None:
            print("Error! You must log in before you are able to cancel an appointment.")
            return None

        # Check if the correct user is logged in as the appointment (caregiver or patient)
        if appointment["patient"] != CURRENT_PATIENT and CURRENT_CAREGIVER is None or \
                appointment["caregiver"] != CURRENT_CAREGIVER and CURRENT_PATIENT is None:
            print("Error! You are only allowed to cancel your own appointment. "
                  "Please login to the correct account first before attempting to cancel.")
            return None

        # Set the date as available (1) in the Availabilities table
        update_availabilities = f"UPDATE Availabilities SET Available=1 " \
                                f"WHERE Time='{appointment['time']}'"
        try:
            cursor.execute(update_availabilities)
            conn.commit()
        except DatabaseUpdateError:
            print("Failed to update appointment details. Please try again.")
            return None

        # Get number of vaccines
        get_vaccine_dosage = f"SELECT Doses FROM Vaccines WHERE Name='{appointment['vaccine']}'"
        vaccine_dosage = None
        try:
            cursor.execute(get_vaccine_dosage)
            for row in cursor:
                vaccine_dosage = row["Doses"]
        except DatabaseRetrievalError:
            print("Unable to get count of vaccine for cancellation. Please try again.")
            return None

        if vaccine_dosage is None:
            print("Unable to get count of vaccine for cancellation. Please try again.")
            return None

        # Update vaccines database
        update_vaccine = f"UPDATE Vaccines SET Doses={vaccine_dosage + 1} " \
                         f"WHERE Name='{appointment['vaccine']}'"
        try:
            cursor.execute(update_vaccine)
            conn.commit()
        except DatabaseUpdateError:
            print("Unable to refund vaccine for cancellation. Please try again.")
            return None

        # Delete appointment from Appointments table
        cancel_appointment = f"DELETE FROM Appointment WHERE ID={appt_id}"
        try:
            cursor.execute(cancel_appointment)
            conn.commit()
        except DatabaseUpdateError:
            print("Failed to cancel appointment. Please try again.")

        print("Successfully canceled your appointment. Please come again!")
    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when canceling appointment.")
        return None
    finally:
        cm.close_connection()


def add_doses(tokens):
    """
    Allows a caregiver to update the amount of doses available for a vaccine
    @param tokens: Expression to run function
    * Token[0]: add_doses
    * Token[1]: <vaccine>
    * Token[2]: <number>
    """

    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global CURRENT_CAREGIVER
    if CURRENT_CAREGIVER is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3
    #  to include all information (with the operation name)
    if len(tokens) != 3:
        print("Invalid input! Please try again making sure you have three arguments: "
              "'add_doses <vaccine> <number>'")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        try:
            vaccine = Vaccine(vaccine_name, doses).get()
        except DatabaseRetrievalError:
            print("Failed to get Vaccine!")
            return
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need
    # to create the vaccine and insert it into the Vaccines table
    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            try:
                vaccine.save_to_db()
            except DatabaseSaveError:
                print("Failed To Save")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            try:
                vaccine.increase_available_doses(doses)
            except DatabaseUpdateError:
                print("Failed to increase available doses!")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")

    print("Doses updated!")


def show_appointments(tokens):
    """
    Prints a user's currently scheduled appointments
    @param tokens: Expression to run function
    * Token[0]: show_appointments
    """

    # Check for valid input
    if len(tokens) != 1:
        print("Invalid input! Please try again making sure you have one argument: "
              "'show_appointments'")
        return None

    # Check if no user is logged in
    if CURRENT_CAREGIVER is None and CURRENT_PATIENT is None:
        print("Please log in before seeing appointments!")
        return None

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    # Check which user is currently logged in
    if CURRENT_PATIENT is not None:
        user_type = "Patient"
        opposite_user = "Caregiver"
        current_user = CURRENT_PATIENT
    else:
        user_type = "Caregiver"
        opposite_user = "Patient"
        current_user = CURRENT_CAREGIVER

    # Get appointments for current user
    get_appointments = f"SELECT * FROM Appointment WHERE {user_type} = '{current_user}'"
    try:
        try:
            cursor.execute(get_appointments)
        except DatabaseRetrievalError:
            print("Failed to print appointments. Please try again.")
            return None
        appointments = list()
        for row in cursor:
            appointments.append([row["ID"], row["Vaccine"], row["Time"], row[f"{opposite_user}"]])
        print(tabulate(appointments,
                       headers=["Appointment ID", "Vaccine", "Date", f"{opposite_user}"]))

    except pymssql.Error as db_err:
        sql_rc = str(db_err.args[0])
        print("Exception code: " + str(sql_rc))
        print("Error occurred when retrieving appointments")
        return None
    finally:
        cm.close_connection()


def logout(tokens):
    """
    Logs the user out from the Scheduler client
    @param tokens: Expression to run function
    * Token[0]: logout
    """
    if len(tokens) != 1:
        print("Invalid input. Please make sure you only have 1 argument: 'logout'")
        return None

    global CURRENT_PATIENT
    global CURRENT_CAREGIVER
    if CURRENT_CAREGIVER is None and CURRENT_PATIENT is None:
        print("Unable to log out as no user is currently logged in!")
        return None

    CURRENT_PATIENT = None
    CURRENT_CAREGIVER = None
    print("Successfully logged out!")


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date (YYYY-MM-DD)>")
        print("> reserve <date (YYYY-MM-DD)> <vaccine>")
        print("> upload_availability <date (YYYY-MM-DD)>")
        print("> cancel <appointment_id>")
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")
        print("> logout")
        print("> Quit")
        print()
        # response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        # response = response.lower()
        tokens = response.split(" ")
        # if tokens[0] != "create_patient" or tokens[0] != "create_caregiver":
        #     tokens = [token.lower() for token in tokens]

        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0].lower()
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    # start command line
    print("\n Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")
    start()
