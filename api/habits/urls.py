from rest_framework.routers import DefaultRouter

from .views import HabitViewSet, StudentPointsViewSet

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habit")
router.register(r"student-points", StudentPointsViewSet, basename="student-points")

urlpatterns = router.urls
