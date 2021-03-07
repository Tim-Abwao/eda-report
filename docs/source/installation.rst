Installation
============

Python versions
---------------

Only **Python3.7 and above** are currently supported. This application might work unexpectedly, if at all, for older versions of Python.

About Virtual Environments
--------------------------
Virtual environments are a great way to ensure that you have the correct verisons of dependencies, and avoid breaking other Python packages in your system. `Learn more`_ 

In UNIX-like operating systems, you can create and activate a virtual environment using::

    python3 -m venv eda_env
    source eda_env/bin/activate

For windows, the commands for the same are::
    
    python3 -m venv eda_env
    eda_env\Scripts\activate

You can then install ``eda_report`` from `PyPI`_ using::

    pip install eda-report


.. _Learn more: https://docs.python.org/3/tutorial/venv.html#virtual-environments-and-packages
.. _PyPI: https://pypi.org/project/eda-report/
