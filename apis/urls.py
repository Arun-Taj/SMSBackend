from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView


router = DefaultRouter()

router.register(r'adminuser', AdminUserViewSet)
router.register(r'school', SchoolViewSet)
router.register(r'student', StudentViewSet)
router.register(r'employee', EmployeeViewSet)


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),       # refresh token
    # path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('logout/', CustomTokenBlacklistView.as_view(), name='token_blacklist'),

]
urlpatterns+=router.urls