"""개발 환경 설정."""

import os

from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-key")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
