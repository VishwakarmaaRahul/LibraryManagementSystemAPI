import pymysql
pymysql.install_as_MySQLdb()


import os

env = os.getenv('DJANGO_ENV', 'development')

if env == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.production')
elif env == 'testing':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.testing')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.development')
