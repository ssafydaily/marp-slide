# syntax=docker/dockerfile:1

############################################
# 1) builder : 의존성만 설치하는 단계
############################################
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# requirements.txt 만 먼저 복사 → 코드가 바뀌어도 이 레이어는 캐시 재사용
COPY requirements.txt .
RUN pip install -r requirements.txt

############################################
# 2) runtime : 실제 운영 이미지
############################################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod

# root 가 아닌 일반 사용자로 실행 (보안)
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app
RUN chown appuser:appuser /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .

# Windows 에서 작성된 CRLF 줄바꿈 제거 → "no such file or directory" 오류 방지
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

USER appuser

# 정적 파일 수집 (빌드 시점에는 DB 가 필요 없음, SECRET_KEY 는 임시값)
RUN DJANGO_SECRET_KEY=build-only-secret python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]

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
