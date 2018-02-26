'''
Alob Project
2016
Author(s): R.Walker

'''

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alob_django.settings")

application = get_wsgi_application()
