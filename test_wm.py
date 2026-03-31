import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oceanwaves_project.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
import re
c = Client()
try:
    c.force_login(User.objects.get(username='test_admin'))
    response = c.get('/billing/wholesale/managers/', HTTP_HOST='127.0.0.1')
    html = response.content.decode()
    m = re.search(r'<title>(.*?)</title>', html)
    print("TITLE =", m.group(1) if m else 'No title')
    m = re.search(r'Exception Value:.*?<pre[^>]*>(.*?)</pre>', html, re.DOTALL)
    print("EXCEPTION =", m.group(1).strip() if m else 'None')
except Exception as e:
    print("Error:", e)
