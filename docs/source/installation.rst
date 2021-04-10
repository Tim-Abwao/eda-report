Installation
============

Python versions
---------------

Only **Python3.7 and above** are currently supported. This application might work unexpectedly, if at all, for older versions of Python.

About Virtual Environments
--------------------------
Virtual environments are a great way to ensure that you have the correct verisons of dependencies, and avoid breaking other Python packages in your system. `Learn more`_ 

In UNIX-like operating systems, you can create and activate a virtual environment using::

    # Create a virtual environment named eda_env
    python3 -m venv eda_env
    # Activate the virtual environment
    source eda_env/bin/activate

In windows, the commands for the same are::
    
    python3 -m venv eda_env
    eda_env\Scripts\activate

You can then install ``eda_report`` from the `Python Package Index`_ using ``pip``::

    pip install eda-report


You could also install the latest version right from the `GitHub repository`_ using::

    pip install https://github.com/tim-abwao/auto-eda/archive/main.tar.gz

Afterwards, head on over to :doc:`quickstart` for help getting started.

.. tip::
    For a more comprehensive report, in HTML format, consider using `pandas_profiling`_.

.. _Learn more: https://docs.python.org/3/tutorial/venv.html#virtual-environments-and-packages
.. _Python Package Index: https://pypi.org/project/eda-report/
.. _pandas_profiling: https://pandas-profiling.github.io/pandas-profiling/docs/master/index.html
.. _GitHub repository: https://github.com/Tim-Abwao/auto-eda
