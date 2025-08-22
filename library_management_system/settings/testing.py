# # library_management_system/settings/testing.py
# from .base import *
#
# DEBUG = True
# SECRET_KEY = "test-secret-key"
#
# # Use in-memory database for tests
# # DATABASES = {
# #     "default": {
# #         "ENGINE": "django.db.backends.sqlite3",
# #         "NAME": ":memory:",
# #     }
# # }
#
# # Faster password hashing during tests
# PASSWORD_HASHERS = [
#     "django.contrib.auth.hashers.MD5PasswordHasher",
# ]
#
# ALLOWED_HOSTS = ["*"]


from .base import *

DEBUG = False
SECRET_KEY = "testing-secret-key"
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # in-memory DB
    }
}

# Optional: faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable migrations for speed (optional)
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()
