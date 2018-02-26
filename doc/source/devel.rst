Setup Development Environment
=============================

Python & Python-Packages
''''''''''''''''''''''''

Install Miniconda 3 from `http://conda.pydata.org/miniconda.html <http://conda.pydata.org/miniconda.html>`_

Create virtual environment

.. code-block:: python

    conda env create -f environment_py3k.yml -n alob_c_env_py3k

MySQL
'''''

If you want to use the MySQL-Database-Server as back-end of the `alob` application.
Install MySQL-Server from `https://dev.mysql.com/downloads/mysql/ <https://dev.mysql.com/downloads/mysql/>`_

.. code-block:: sql

    CREATE DATABASE alob;
    CREATE USER 'alob'@'localhost' IDENTIFIED BY 'alob';
    GRANT ALL PRIVILEGES ON alob.* TO 'alob'@'localhost';
    FLUSH PRIVILEGES;

Configuration of virtual environment
''''''''''''''''''''''''''''''''''''

Now the virtual environment can be started with:

.. code-block:: python

    lnx> source activate alob_c_env_py3k
    win> activate alob_c_env_py3k

To finish the setup you have to add a ``.pth`` file that the alob modules can be found by the python interpreter:


.. code-block:: python

    conda develop .


Setup Alob Database
'''''''''''''''''''


Create the tables in the alob database:

.. code-block:: python

    python manage.py makemigrations
    python manage.py makemigrations image pair prediction
    python manage.py migrate

    
Running
'''''''


Start the conda environment for `alob`.

.. code-block:: python

    lnx> source activate alob_c_env_py3k
    win> activate alob_c_env_py3k

Start the development-server for the web-front-end:

.. code-block:: python
    
    > pyton manage.py runserver


To open the web-front-end in your preferred browser type `http:localhost:8000 <http:localhost:8000>`_ in the address bar. 
