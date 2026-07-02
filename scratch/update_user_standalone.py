import os
import sys
import django

# Set up the Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focustube.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import UserProfile

username = 'aryamaddy_1'
password = 'TTMLVA4bjw88yKR'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"User {username} already exists. Password updated.")
except User.DoesNotExist:
    user = User.objects.create_user(username=username, password=password)
    print(f"User {username} created.")

profile = user.profile
profile.plan_type = 'pro'
profile.save()
print(f"Premium access (pro) granted to {username}.")
