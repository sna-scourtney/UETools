# UETools Development Environment

The author develops this package on Linux, but it should
be possible to work on other platforms as long as the
Python dependencies are met.

Please refer to the [Notations](Notations.md) page for a
description of the notational conventions used here.

## Python Interpreter

Python 3.13 or newer is recommended, but the project is
probably compatible with Python 3.10 or later. There is
no intent to backport to versions prior to 3.13, but
feel free to submit a PR (pull request) if you undertake
this task.

## Virtual Environment

The use of a virtual environment is *strongly* recommended
to avoid interfering with the system Python installation.
On Linux, this can be achieved with the following command:

    $ cd some_directory/UETools.git/
    $ python3 -m venv venv</code>

