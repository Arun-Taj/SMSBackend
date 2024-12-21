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
    path('get_income_heads/', get_income_heads, name='get_income_heads'),
    path('get_expense_heads/', get_expense_heads, name='get_expense_heads'),
    path('add_income_expense/', add_income_expense, name='add_income_expense'),
    path('get_income_expenses/', get_income_expenses, name='get_income_expenses'),
    path('delete_income_expense/<int:id>/', delete_income_expense, name='delete_income_expense'),




    #exams
    path('exam_sessions/', get_exam_sessions, name="get_exam_sessions"),
    path('get_class_subjects/', get_class_subjects, name="get_class_subjects"),
    path('configure_exam_papers/', configure_exam_papers, name="configure_exam_papers"),
    path('get_exams/<int:exam_session_id>/', get_exams, name="get_exams"),
    path('delete_exam/<int:exam_id>/', delete_exam, name="delete_exam"),
    path('get_exam_papers/<int:exam_id>/', get_exam_papers, name="get_exam_papers"),
    path('delete_exam_paper/<int:paper_id>/', delete_exam_paper, name="delete_exam_paper"),
    path('update_exam_papers/', update_exam_papers, name="update_exam_papers"),
    path('get_exams_classes/<int:exam_id>/', get_exams_classes, name="get_exams_classes"),
    path('get_students_with_marks/<int:exam_id>/<int:class_id>/',get_students_with_marks, name="get_students_with_marks"),
    path('get_subjects_for_this_exam/<int:exam_id>/<int:class_id>/',get_subjects_for_this_exam, name="get_subjects_for_this_exam"),



    #students
    path('get_students_for_marks_entry/<int:exam_id>/<int:class_id>/', get_students_for_marks_entry, name="get_students_for_marks_entry"),
    path('update_marks/', update_marks, name="update_marks"),
    path('get_student_by_enr_no/<int:exam_id>/<int:class_id>/<enr_no>/', get_student_by_enr_no, name="get_student_by_enr_no"),


    #result
    path('get_student_report/<int:exam_id>/<search_key>/', get_student_report, name="get_student_report"),
    path('get_marks/<int:exam_id>/<int:class_id>/', get_marks, name="get_marks"),

]
urlpatterns+=router.urls