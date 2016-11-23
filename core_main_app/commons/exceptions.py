""" Core Exceptions
"""


class CoreError(Exception):
    """ Exception raised by the Core
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ApiError(Exception):
    """ Exception raised by the API
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ModelError(Exception):
    """ Generic exception for the model
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class DoesNotExist(Exception):
    """ Exception raised when an object does not exist
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class XMLError(Exception):
    """ Exception raised by XML validation
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class XSDError(Exception):
    """ Exception raised by XSD validation
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
