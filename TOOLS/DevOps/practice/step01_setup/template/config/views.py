from django.db import DatabaseError, connection  # noqa: F401
from django.http import JsonResponse  # noqa: F401


def health(request):
    """서버와 DB 상태를 확인하는 헬스체크 엔드포인트."""
    # TODO 2: DB 에 "SELECT 1" 쿼리를 실행해 연결을 확인하세요.
    #   - 성공: {"status": "ok", "database": "ok"}       (200)
    #   - 실패: {"status": "error", "database": "error"} (503)
    #   힌트: with connection.cursor() as cursor: cursor.execute("SELECT 1")
    raise NotImplementedError
