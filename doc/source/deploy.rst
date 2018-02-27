Deploy the Alob/Server
======================

The Alob-Server is deployed with `docker <https://www.docker.com/>`_, `nginx <https://nginx.org/>`_ and `gunicorn <http://gunicorn.org/>`_.

How to deploy Alob in the cloud.
This documentation is valid for `Ubuntu 16.04.3 LTS <https://www.ubuntu.com/server>`_ 

Update
------

Update the machine and clear old packages.

.. code-block:: python

    sudo apt-get update
    sudo apt-get -y upgrade
    sudo apt-get -y dist-upgrade
    sudo apt autoremove

Docker
------

.. code-block:: python

    sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    sudo apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'
    sudo apt-get update
    sudo apt-get install -y docker-engine

Docker-Compose
--------------

.. code-block:: python

    sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.19.0/docker-compose-$(uname -s)-$(uname -m)"
    sudo chmod +x /usr/local/bin/docker-compose

    sudo usermod -aG docker ubuntu

Checkout Sources
----------------

.. code-block:: python

    git clone SOURCE_LINK


Setup
-----

.. code-block:: python

    cd alob
    cd data
    sudo ln -s ../alob_django/media/ .
    cd ..
    docker-compose up -d
    docker-compose exec web /bin/bash
    web> python manage.py makemigrations image pair prediction
    web> python manage.py migrate
    web> python loaddata dump.json

Make sure that *ALLOWED_HOST* is correctly set in *alob_django/alob_django/settings.py*.



Backup
------

Database
````````

There is a python script `backup_db.py` that have to be adapted to be used in your environment.
If you have a S3-compatible object storage, the user credentials have to be adapted.

.. code-block:: python

    sudo apt-get install -y python3-boto3

.. code-block:: python

    crontab -e
    # every day at 2am
    0 2 * * * /usr/bin/python3 /home/ubuntu/alob/backup_db.py > /home/ubuntu/alob/log/backup.log 2>&1

Data
````

The script `backup_data.py` can be used to create a zipped tar-archive of the data-folder to be used
as a backup of the user data.





    