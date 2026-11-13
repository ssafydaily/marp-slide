from django.db import DatabaseError, connection
from django.http import JsonResponse


def health(request):
    """서버와 DB 상태를 확인하는 헬스체크 엔드포인트."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return JsonResponse({"status": "error", "database": "error"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})
