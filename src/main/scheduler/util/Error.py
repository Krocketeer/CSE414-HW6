"""
* Kenny "Ackerson" Le
* 11/28/21
* CSE 414: HW6 — Vaccine Scheduler
* Description: Custom defined errors to throw for Scheduler.py when accessing the database
"""


class Error(Exception):
    """
    Base class for other exceptions
    """
    pass


class DatabaseSaveError(Error):
    """
    Raised when unable to save information to database
    """
    pass


class DatabaseUpdateError(Error):
    """
    Raised when unable to upload appointment to database
    """
    pass


class DatabaseRetrievalError(Error):
    """
    Raised when failed to retrieve information from database
    """
    pass


