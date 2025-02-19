from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(AdminUser)
admin.site.register(School)
admin.site.register(Student)
admin.site.register(Employee)
admin.site.register(Class)
# @admin.register(Class)
# class ClassAdmin(admin.ModelAdmin):
#     list_display = ['id','className']

admin.site.register(Subject)
admin.site.register(ClassSubject)
admin.site.register(ChartOfAccount)
admin.site.register(IncomeExpense)
admin.site.register(ExamSession)
admin.site.register(Exam)
admin.site.register(ExamPaper)
admin.site.register(ObtainedMark)
admin.site.register(Month)
admin.site.register(Receipt)
admin.site.register(Attendance)
admin.site.register(EmployeeAttendance)
admin.site.register(Role)

