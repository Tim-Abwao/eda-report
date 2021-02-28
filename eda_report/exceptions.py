class Error(Exception):
    """Base class for exceptions in this package."""
    pass


class InputError(Error):
    """Exception raised for invalid input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
