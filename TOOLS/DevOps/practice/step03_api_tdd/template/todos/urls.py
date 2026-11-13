from rest_framework.routers import DefaultRouter

from todos.views import TodoViewSet  # noqa: F401

router = DefaultRouter()
# TODO 4: router 에 "todos" 경로로 TodoViewSet 을 등록하세요. (basename="todo")

urlpatterns = router.urls
