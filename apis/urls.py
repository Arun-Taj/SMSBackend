from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'adminuser', views.AdminUserViewSet)
router.register(r'school', views.SchoolViewSet)


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),       # refresh token




]

from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns += [
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]

urlpatterns+=router.urls