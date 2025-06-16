from rest_framework.routers import DefaultRouter
from api.tags.views import TagViewSet

router = DefaultRouter()
router.register(r'', TagViewSet, basename='tag')

urlpatterns = router.urls
