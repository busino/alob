Setup Development Environment
=============================

Python & Python-Packages
''''''''''''''''''''''''

Download and install *Miniconda* for Python (>=3.6) from `http://conda.pydata.org/miniconda.html <http://conda.pydata.org/miniconda.html>`_

Create virtual environment

::

    conda env create -f environment_py3k.yml -n alob_c_env_py3k

MySQL
'''''

If you want to use the MySQL-Database-Server as back-end of the `alob` application.
Install MySQL-Server from `https://dev.mysql.com/downloads/mysql/ <https://dev.mysql.com/downloads/mysql/>`_

::

    CREATE DATABASE alob;
    CREATE USER 'alob'@'localhost' IDENTIFIED BY 'alob';
    GRANT ALL PRIVILEGES ON alob.* TO 'alob'@'localhost';
    FLUSH PRIVILEGES;

Configuration of virtual environment
''''''''''''''''''''''''''''''''''''

Now the virtual environment can be started with:

::

    lnx> source activate alob_c_env_py3k
    win> activate alob_c_env_py3k

To finish the setup you have to add a ``.pth`` file that the alob modules can be found by the python interpreter:


::

    conda develop .


Change settings
'''''''''''''''

The django-settings are set for *production* per default.
Change variable *DEPLOY_TYPE* in *alob_django/alob_django/settings.py* to *dev* for development.

::

    DEPLOY_TYPE = 'dev'


Setup Alob Database
'''''''''''''''''''

Create the tables in the alob database:

::

    python manage.py makemigrations
    python manage.py makemigrations image pair prediction
    python manage.py migrate

    
Running
'''''''


Start the conda environment for `alob`.

::

    lnx> source activate alob_c_env_py3k
    win> activate alob_c_env_py3k

Start the development-server for the web-front-end:

::
    
    pyton manage.py runserver


To open the web-front-end in your preferred browser type `http:localhost:8000 <http:localhost:8000>`_ in the address bar. 
