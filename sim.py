import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oceanwaves_project.settings')
django.setup()
from pos.models import UserProfile, AreaManagerStore, Store
try:
    p = UserProfile.objects.get(user__username='punith_area')
    print("User profile store:", p.store)
    am_links = AreaManagerStore.objects.filter(store=p.store, manager__is_active=True).select_related('manager__user')
    print("Manager links:", list(am_links))
    managers_ready = []
    managers_no_email = []
    for link in am_links:
        am = link.manager
        name = am.user.get_full_name() or am.user.username
        if am.user.email:
            managers_ready.append({'id': am.id, 'name': name})
        else:
            managers_no_email.append(name)
    print("Ready:", managers_ready)
    print("No Email:", managers_no_email)
except Exception as e:
    print("Error:", e)
