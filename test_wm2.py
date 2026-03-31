import django, os, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oceanwaves_project.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
c = Client()
try:
    c.force_login(User.objects.get(username='test_admin'))
    response = c.get('/billing/wholesale/managers/', HTTP_HOST='127.0.0.1')
    print("Content:", response.content.decode())
except Exception as e:
    print("Error:", e)
