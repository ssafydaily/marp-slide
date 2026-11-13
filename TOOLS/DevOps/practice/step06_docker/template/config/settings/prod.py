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

# TODO 9: whitenoise 로 정적 파일을 서빙하도록 설정하세요.
#   - MIDDLEWARE 의 SecurityMiddleware 바로 다음(인덱스 1)에
#     "whitenoise.middleware.WhiteNoiseMiddleware" 추가  (# noqa: F405)
#   - STORAGES["staticfiles"]["BACKEND"] =
#     "whitenoise.storage.CompressedManifestStaticFilesStorage"
