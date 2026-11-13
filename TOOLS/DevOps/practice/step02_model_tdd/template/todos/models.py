from django.db import models  # noqa: F401

# TODO 2: tests/test_models.py 를 통과하도록 Todo 모델을 작성하세요.
#
#   필드
#     - title       : 최대 200자 문자열
#     - description : 긴 텍스트, 비워둘 수 있음
#     - is_done     : 불리언, 기본값 False
#     - created_at  : 생성 시각 자동 저장
#     - updated_at  : 수정 시각 자동 저장
#
#   Meta
#     - 최신 항목이 먼저 오도록 정렬 (["-created_at", "-id"])
#
#   메서드
#     - __str__   : title 반환
#     - mark_done : is_done 을 True 로 바꾸고 저장
#
# TODO 3: 모델 작성 후 마이그레이션 생성 & 적용
#     python manage.py makemigrations todos
#     python manage.py migrate
