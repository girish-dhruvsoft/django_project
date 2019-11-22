"""
WSGI config for SFConnection project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
os.environ["SECRET_KEY"] ='=_d*o-jfac+gh%4eaxbxv^0c^0)q)fasp7p^ls3i#nxp#u!&dz'
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SFConnection.settings')

application = get_wsgi_application()
