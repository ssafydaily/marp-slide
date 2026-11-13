"""운영 환경 설정: 모든 비밀값은 반드시 환경변수로 주입한다."""

import os

from .base import *  # noqa: F403


def env_list(name):
    """'a,b,c' 형태의 환경변수를 리스트로 변환한다."""
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


DEBUG = False

# 값이 없으면 KeyError 로 즉시 실패 → 잘못된 설정으로 운영되는 것을 막는다
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# 정적 파일: whitenoise 가 gunicorn 에서 직접 서빙한다 (Nginx 설정 단순화)
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Nginx(리버스 프록시) 뒤에서 동작할 때 원래 요청의 프로토콜 정보를 신뢰한다
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
