#!/bin/bash
python manage.py collectstatic && gunicorn --workers 2 kodak_transport.wsgi