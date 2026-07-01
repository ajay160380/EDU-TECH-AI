import sys
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

# The profile should be created by the post_save signal.
profile = user.profile
profile.plan_type = 'pro'  # Giving 'pro' premium access
profile.save()
print(f"Premium access (pro) granted to {username}.")
