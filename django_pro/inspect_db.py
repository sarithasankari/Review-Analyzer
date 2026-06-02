
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE app_userprofile;")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
