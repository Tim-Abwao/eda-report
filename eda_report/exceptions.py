class Error(Exception):
    """The base class for exceptions in this package."""
    pass


class InputError(Error):
    """The Exception raised when a given input object is invalid.
    """

    def __init__(self, message):
        """Initialise an instance of :class:`InputError`.

        :param message: A brief description of the mishap detected.
        :type message: str
        """
        self.message = message
