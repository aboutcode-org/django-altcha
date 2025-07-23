INSTALLED_APPS = [
    "django_altcha",
]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}
ROOT_URLCONF = "tests.urls"
ALTCHA_HMAC_KEY = "altcha-insecure-hmac-0123456789abcdef"
