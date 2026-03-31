import re
with open('test_wm.py') as f: pass
from test_wm import c, User
c.force_login(User.objects.get(username='test_admin'))
response = c.get('/billing/wholesale/managers/')
m = re.search(r'<title>(.*?)</title>', response.content.decode())
print("Title:", m.group(1) if m else 'No title')
m = re.search(r'Exception Value:\s*(.*?)<', response.content.decode())
print("Exception:", m.group(1) if m else 'No exception')
