# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProyectoBack.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@gmail.com',
        password='1234'
    )
else:
    user = User.objects.get(username='admin')
    user.set_password('1234')
    user.save()

