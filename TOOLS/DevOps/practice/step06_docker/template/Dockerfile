# syntax=docker/dockerfile:1

############################################
# 1) builder : 의존성만 설치하는 단계
############################################
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# TODO 1: requirements.txt 만 먼저 복사하고 pip install 하세요.
#   (코드보다 먼저 복사해야 레이어 캐시가 재사용됩니다)


############################################
# 2) runtime : 실제 운영 이미지
############################################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod

RUN useradd --create-home --uid 1000 appuser
WORKDIR /app
RUN chown appuser:appuser /app

# TODO 2: builder 단계의 /opt/venv 를 복사하세요.  (COPY --from=builder ...)

# TODO 3: 소스 코드를 appuser 소유로 복사하세요.   (COPY --chown=appuser:appuser . .)

# Windows 에서 작성된 CRLF 줄바꿈 제거 → "no such file or directory" 오류 방지
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

USER appuser

# TODO 4: collectstatic 을 실행하세요. (SECRET_KEY 는 빌드용 임시값을 넘겨줍니다)
#   RUN DJANGO_SECRET_KEY=build-only-secret python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
# TODO 5: gunicorn 으로 config.wsgi:application 을 0.0.0.0:8000 에서 실행하세요.
CMD []

############################################
# 3) test : 컨테이너 안에서 pytest 를 실행하는 이미지
############################################
FROM runtime AS test

ENV DJANGO_SETTINGS_MODULE=config.settings.dev \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

USER root
RUN pip install -r requirements-dev.txt
USER appuser

CMD ["pytest"]
