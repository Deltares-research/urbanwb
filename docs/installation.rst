Installation
************
Prerequisite
------------
Urbanwb currently requires Python 3.6+ to run. Please install Python 3.6+ if it is not ready.
Python uses ``pip`` for installing additional software packages.
We recommend installing these modules into your home directory via ``--user``,
or into a `virtual environment <https://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/>`_ via ``virtualenv``.


Dependencies
------------
In order to run urbanwb model requires the following packages:

+ numpy
+ pandas
+ toml
+ fire
+ tqdm

Once the urbanwb module is being installed, it will automatically check whether the package requirement is satisfied. If not,
it will ask for installation of above packages, please check ``Y`` then.

Windows
-------
The best way to install urbanwb is to use the ``setup.py`` install script (found in the urbanwb directory) with ``python setup.py install``,

however it is recommended to do as followings:

First, clone with git or download the latest zip with the source code of urbanwb.

Then, go to the urbanwb directory and run with cmd:

.. code-block:: python

    pip install -e .

To check whether install is successfull, go to and run: this should run without errors
(this may be added in the future.)

Linux
-----
to be added ?.



