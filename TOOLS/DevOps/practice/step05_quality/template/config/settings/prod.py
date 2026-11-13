"""운영 환경 설정: 모든 비밀값은 반드시 환경변수로 주입한다."""

# TODO 3: base.py 의 공통 설정을 가져오세요.

# TODO 4: 운영 환경 값을 설정하세요.
#   - DEBUG = False
#   - SECRET_KEY : os.environ["DJANGO_SECRET_KEY"]  (없으면 실행 실패 → 의도된 동작)
#   - ALLOWED_HOSTS        : 환경변수 DJANGO_ALLOWED_HOSTS ("a,b,c" → 리스트)
#   - CSRF_TRUSTED_ORIGINS : 환경변수 DJANGO_CSRF_TRUSTED_ORIGINS
