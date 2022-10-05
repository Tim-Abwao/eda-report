class Error(Exception):
    """The base class for exceptions in this package."""

    pass


class InputError(Error):
    """The *Exception* raised when a given input object is *not of the
    expected type* or is otherwise *invalid*.

    In most cases, an attempt is made to cast the erroneous input into the
    proper type, and this *Exception* is raised if it fails.

    Args:
        message (str): A brief description of the mishap detected.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class EmptyDataError(InputError):
    """The *Exception* raised when an iterable input object has length zero
    or has no items to yield.
    """

    pass


class GroupbyVariableError(InputError):
    """The *Exception* raised when the specified group-by variable is invalid.
    """

    pass
