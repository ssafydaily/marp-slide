from rest_framework.routers import DefaultRouter

from todos.views import TodoViewSet

router = DefaultRouter()
router.register("todos", TodoViewSet, basename="todo")

urlpatterns = router.urls
