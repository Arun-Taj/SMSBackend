from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from .import models
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def reconfigure_rollNo(class_name):
    # print(class_name)
    students = models.Student.objects.filter(classOfAdmission=class_name).order_by('studentFirstName')
    for new_rollNo, student in enumerate(students, start=1):
        student.rollNo = new_rollNo
        student.save()



def validate_and_set_password(user, new_password):
    # Validate the new password
    validate_password(new_password, user)

    # If validation passes, set the new password
    user.set_password(new_password)

    return user



def get_subjects_for_exam(request, exam_id, class_id):
    try:
        class_name = models.Class.objects.get(id=class_id)
    except models.Class.DoesNotExist:
        return
        

    try:
        # Prefetch only the needed fields, applying filter directly in the query
        exam = models.Exam.objects.prefetch_related(
            'exam_papers__subject__class_name'  # Prefetch the class_name related to each subject
        ).get(id=exam_id)
    except models.Exam.DoesNotExist:
        return

    # Filter and select the needed data using `values` to avoid unnecessary data fetching
    this_class_papers = [
        paper for paper in exam.exam_papers.filter(subject__class_name__id=class_id).annotate(subject_name=F('subject__subject__subjectName')).values('id', 'subject_name')
    ]

    return this_class_papers
