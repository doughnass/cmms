import os
import sys
import traceback

# adjust path
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')

import django
from django.test.client import RequestFactory

try:
    django.setup()
    from cmms import views
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # get or create a user
    user, _ = User.objects.get_or_create(username='__debug_user__', defaults={'email':'debug@example.com'})
    # mark user active
    user.is_active = True
    user.save()

    rf = RequestFactory()
    req = rf.get('/my-service-requests')
    # set a user on request that passes login_required
    req.user = user

    # call the view
    resp = views.my_service_requests(req)
    print('View returned:', type(resp), getattr(resp, 'status_code', None))
    if hasattr(resp, 'content'):
        print(resp.content[:1000])
except Exception:
    print('Exception when calling view:')
    traceback.print_exc()
    sys.exit(1)
