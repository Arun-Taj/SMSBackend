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
router.register(r'class', ClassViewSet)
router.register(r'subject', SubjectViewSet)
router.register(r'class_subject', ClassSubjectViewSet)


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),       # refresh token
    # path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('logout/', CustomTokenBlacklistView.as_view(), name='token_blacklist'),


    path('get_classes/', get_classes, name='get_classes'),
    path('get_subjects/<int:class_id>/', get_subjects, name='get_subjects'),
    path('get_teachers/', get_teachers, name='get_teachers'),
    path('get_assigned_subject_classes/', get_assigned_subject_classes, name='get_assigned_subject_classes'),


    #for config
    path('get_classes_for_config/', get_classes_for_config, name='get_classes_for_config'),
    path('get_subjects_for_config/', get_subjects_for_config, name='get_subjects_for_config'),
    path('get_teachers_for_config/', get_teachers_for_config, name='get_teachers_for_config'),
    path('assign_subjects_to_class/', assign_subjects_to_class, name='assign_subjects_to_class'),
    path('get_classes_and_subjects/', get_classes_and_subjects, name='get_classes_and_subjects'),
    path('update_class_subjects/', update_class_subjects, name='update_class_subjects'),



    #Accounts
    path('get_chart_of_accounts/', get_chart_of_accounts, name='get_chart_of_accounts'),
    path('add_chart_of_accounts/', add_chart_of_accounts, name='add_chart_of_accounts'),
    path('delete_chart_of_accounts/<int:id>/', delete_chart_of_accounts, name='delete_chart_of_accounts'),

]
urlpatterns+=router.urls