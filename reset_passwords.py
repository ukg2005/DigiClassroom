from django.contrib.auth import get_user_model
User = get_user_model()
target_usernames = ['rajeshkumar', 'priyavenkataraman', 'sureshnaidu', 'anithareddy', 'udaykiran', 'karthik', 'sarathchandra', 'varunkalidindi', 'sudharshanpaul']
users_to_reset = User.objects.filter(is_superuser=False).filter(username__in=target_usernames) | User.objects.filter(is_superuser=False).filter(username__startswith='teacher') | User.objects.filter(is_superuser=False).filter(username__startswith='student')
count = 0
for user in users_to_reset:
    user.set_password('demo12345')
    user.save()
    count += 1
uday = User.objects.filter(username='udaykiran').first()
exists = uday is not None
is_correct = uday.check_password('demo12345') if exists else False
print(f"udaykiran exists: {exists}")
print(f"udaykiran check_password('demo12345'): {is_correct}")
print(f"Users reset: {count}")
