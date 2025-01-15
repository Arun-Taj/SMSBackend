from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

from rest_framework.permissions import IsAuthenticated, AllowAny
from . import serializers
from rest_framework import viewsets
from . import models
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view

from django.db.models import F, Value, Count, Case, When, Sum

from django.db.models.functions import Concat
from collections import defaultdict
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from django.db import transaction





@api_view(['GET'])
def get_school_data(request):

    if not request.user.is_authenticated:
        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        school = request.user.school
    except models.School.DoesNotExist:
        return Response({"message": "School not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        school_data = serializers.SchoolSerializer(school).data
        admin_data = serializers.AdminUserSerializer(request.user).data
        return Response({"school": school_data, "admin": admin_data}, status=status.HTTP_200_OK)



class CustomTokenBlacklistView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return JsonResponse({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            # Blacklist the refresh token
            token.blacklist()
            print("tried to blacklist")
            return JsonResponse({'detail': 'Token blacklisted successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = models.AdminUser.objects.all()

    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads


    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return serializers.UpdateAdminUserSerializer
        return serializers.AdminUserSerializer


    def get_permissions(self):
        """
        Overrides permissions for specific actions. The create method allows
        anyone to access it, while other methods require authentication.
        """
        if self.action == 'create':
            # Allow anyone to create
            return [AllowAny()]
        return [IsAuthenticated()]  # Restrict other actions to authenticated users

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # print(request.data)
        user = serializer.save()  # This calls the create method in the serializer
        headers = self.get_success_headers(serializer.data)

        # Custom response after successful signup
        return Response(
            {"message": "User created successfully", "user": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )




class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_permissions(self):
        """
        Overrides permissions for specific actions. The create method allows
        anyone to access it, while other methods require authentication.
        """
        if self.action == 'create':
            # Allow anyone to create
            return [AllowAny()]

        return [IsAuthenticated()]  # Restrict other actions to authenticated users
    





class StudentViewSet(viewsets.ModelViewSet):
    queryset = models.Student.objects.all()  
    serializer_class = serializers.StudentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # raise PermissionError('User is not authenticated')
            return models.Student.objects.none()

        return super().get_queryset().filter(school=self.request.user.school).order_by('studentFirstName')
    


@api_view(["POST"])
def promote_student(request):

    try:
        for student_data in request.data:
            student_id = student_data['id']
            student = models.Student.objects.get(id=student_id)
            if student.classOfAdmission.id != int(student_data['classOfAdmission']):
                print(student.student_full_name)
                promoted_class = models.Class.objects.get(id=student_data['classOfAdmission'])
                student.classOfAdmission = promoted_class
                student.save(promoting=True)
    except Exception as e:
        return Response({"message": "Failed to promote students"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message": "Students promoted successfully"}, status=status.HTTP_200_OK)



class UpdateStudentView(APIView):
    def put(self, request, *args, **kwargs):
        student_id = kwargs.get('id')
        try:
            student = models.Student.objects.get(id=student_id)
        except models.Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize incoming data (including file data) for updating the student instance
        serializer = serializers.StudentUpdateSerializer(student, data=request.data, context={'request': request})

        if serializer.is_valid():
            # Perform the update
            serializer.save()
            return Response({"detail": "Student updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'school'):
                return super().get_queryset().filter(school=self.request.user.school).order_by('employeeFirstName')
            else:
                return models.Employee.objects.none()  # or handle the error if necessary
        else:
            return models.Employee.objects.none()

    def create(self, request, *args, **kwargs):
        print(request.data)
        complementary_subjects = [int(subject_id) for subject_id in request.data['complementarySubjects'].split(",")]
        request.data.pop('complementarySubjects', None)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # Log validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        employee = serializer.save()
        employee.complementarySubjects.set(complementary_subjects)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    #for update
    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            complementary_subjects = [int(subject_id) for subject_id in data['complementarySubjects'].split(",")]
        except:
            complementary_subjects = []
        data.pop('complementarySubjects', None)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        if not serializer.is_valid():
            print(serializer.errors)  # Log validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        employee = serializer.save()
        employee.complementarySubjects.set(complementary_subjects)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ClassViewSet(viewsets.ModelViewSet):
    queryset = models.Class.objects.all()
    serializer_class = serializers.ClassSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(school=self.request.user.school).prefetch_related('class_teacher')
        else:
            # raise PermissionError('User is not authenticated')
            return models.Class.objects.none()




class SubjectViewSet(viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(school=self.request.user.school)
        else:
            # raise PermissionError('User is not authenticated')
            return models.Subject.objects.none()





class ClassSubjectViewSet(viewsets.ModelViewSet):
    queryset = models.ClassSubject.objects.all()
    serializer_class = serializers.ClassSubjectSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return (
                super()
                .get_queryset()
                .filter(subject__school=self.request.user.school)
                .select_related('subject_teacher')
                .prefetch_related('subject', 'class_name')
            )
    
        else:
            # raise PermissionError("User is not authenticated")
            return models.ClassSubject.objects.none()
        

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
        
    #     # Grouping data by class name
    #     grouped_data = {}
    #     for item in serializer.data:
    #         class_name = item['class_name']['className']
    #         subject_name = item['subject']['subjectName']
    #         teacher_name = f"{item['subject_teacher']['employeeFirstName']} {item['subject_teacher']['employeeLastName']}"
            
    #         if class_name not in grouped_data:
    #             grouped_data[class_name] = {
    #                 "className": class_name,
    #                 "subjects": []
    #             }
            
    #         grouped_data[class_name]["subjects"].append({
    #             "subject": subject_name,
    #             "teacher": teacher_name
    #         })

    #     # Convert the grouped data to a list
    #     formatted_response = list(grouped_data.values())

    #     return Response(formatted_response)



class RoleListView(ListAPIView):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer

@api_view(['GET'])
def get_assigned_subject_classes(request):
    class_subjects = models.ClassSubject.objects.filter(
        subject__school=request.user.school
    ).all()
    serializer = serializers.GETClassSubjectSerializer(class_subjects, many=True,  context={'request': request})
    # Grouping data by class name
    grouped_data = {}
    for item in serializer.data:
        class_name = item['class_name']['className']
        subject_name = item['subject']['subjectName']
        teacher_name = f"{item['subject_teacher']['employeeFirstName']} {item['subject_teacher']['employeeLastName']}"
        
        if class_name not in grouped_data:
            grouped_data[class_name] = {
                "className": class_name,
                "subjects": []
            }
        
        grouped_data[class_name]["subjects"].append({
            "subject": subject_name,
            "teacher": teacher_name
        })

    # Convert the grouped data to a list
    formatted_response = list(grouped_data.values())

    return Response(formatted_response)


@api_view(['GET'])
def get_classes(request):
    classes = models.Class.objects.values('id', 'className')
    return Response(classes)




@api_view(['GET'])
def get_subjects(request, class_id):
    # subjects = models.ClassSubject.objects.filter(class_name__school=request.user.school).filter(class_name=class_id).values('id', 'subject__subjectName')
    subjects = models.Subject.objects.filter(
    school=request.user.school
    ).values('id', 'subjectName')  # Use the alias instead
    return Response(subjects)




@api_view(['GET'])
def get_teachers(request):
    teachers = models.Employee.objects.filter(school=request.user.school)
    serializer = serializers.SimpleEmployeeSerializer(teachers, many=True)
    return Response(serializer.data)




@api_view(['GET'])
def get_classes_for_config(request):
    # Using annotate to rename the field
    classes = models.Class.objects.filter(school=request.user.school).annotate(name=F('className')).values('id', 'name')
    return Response(list(classes))




@api_view(['GET'])
def get_subjects_for_config(request):
   
    subjects = models.Subject.objects.filter(
    school=request.user.school
    ).annotate(name=F('subjectName')).values('id', 'name')  # Use the alias instead
    return Response(list(subjects))




@api_view(['GET'])
def get_teachers_for_config(request):
    teachers = models.Employee.objects.filter(school=request.user.school)
    serializer = serializers.SimpleEmployeeSerializer(teachers, many=True)

    # Rename 'full_name' to 'name' in the serialized data
    serialized_data = serializer.data
    for item in serialized_data:
        item['name'] = item.pop('full_name')

        
    return Response(list(serialized_data))




@api_view(['POST'])
def assign_subjects_to_class(request):
    data = request.data
    # print(data)
    """
    {'class_id': 1, 'subjects': [{'subjectId': '2', 'teacherId': '1'}]}
    """
    try:
        class_name = models.Class.objects.get(id=data['class_id'])
    except models.Class.DoesNotExist:
        return Response({"error": "Class does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    for item in data['subjects']:
        try:
            subject = models.Subject.objects.get(id=item['subjectId'])
            subject_teacher = models.Employee.objects.get(id=item['teacherId'])
        except models.Subject.DoesNotExist or models.Employee.DoesNotExist:
            return Response({"error": "Subject or teacher does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            class_subject = models.ClassSubject.objects.get(subject=subject, class_name=class_name)
            return Response({"error": f"Subject {subject.subjectName} already assigned to class {class_name.className}"}, status=status.HTTP_400_BAD_REQUEST)
        except models.ClassSubject.DoesNotExist:
            models.ClassSubject.objects.create(subject=subject, class_name=class_name, subject_teacher=subject_teacher)
        
            
    return Response({"message": "Subjects assigned successfully"}, status=status.HTTP_201_CREATED)





@api_view(['GET'])
def get_classes_and_subjects(request):
    class_subjects = models.ClassSubject.objects.filter(
        subject__school=request.user.school
    ).all()
    data_dict = {}

    for item in class_subjects:
        id = item.class_name.id
        name = item.class_name.className

        # Check if the class ID already exists in the dictionary
        if id not in data_dict:
            # If it doesn't exist, initialize the entry
            data_dict[id] = {
                'id': id,
                'name': name,
                'subjects': []
            }

        # Add the subject to the existing entry
        data_dict[id]['subjects'].append({
            'class_subject_id': item.id,
            'subjectId': item.subject.id,
            'teacherId': item.subject_teacher.id
        })


    # Convert the dictionary back to a list
    data = list(data_dict.values())

    return Response(data)



@api_view(['POST'])
def update_class_subjects(request):
    
    for item in request.data:
        class_subject = models.ClassSubject.objects.get(id=item['class_subject_id'])
        class_subject.subject = models.Subject.objects.get(id=item['subjectId'])
        class_subject.subject_teacher = models.Employee.objects.get(id=item['teacherId'])
        class_subject.save()

    return Response({"message": "Class subjects updated successfully"},status=status.HTTP_200_OK)






@api_view(['GET'])
def get_chart_of_accounts(request):
    chart_of_accounts = models.ChartOfAccount.objects.filter(school=request.user.school).order_by('-created_at').values()
    return Response(chart_of_accounts)



@api_view(['POST'])
def add_chart_of_accounts(request):
    data = request.data
    head  = data['head']
    type = data['type']
    school = request.user.school
    
    created = models.ChartOfAccount.objects.create(head=head, type=type, school=school)

    if created:
        return Response({"message": "Chart of account created successfully"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Failed to create chart of account"}, status=status.HTTP_400_BAD_REQUEST)
  



@api_view(['DELETE'])
def delete_chart_of_accounts(request, id):
    deleted = models.ChartOfAccount.objects.filter(id=id).delete()
    if deleted:
        return Response({"message": "Chart of account deleted successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to delete chart of account"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def get_income_heads(request):
    income_heads = models.ChartOfAccount.objects.incomes().filter(school=request.user.school).values('id', 'head')
    return Response(income_heads)


@api_view(['GET'])
def get_expense_heads(request):
    expense_heads = models.ChartOfAccount.objects.expenses().filter(school=request.user.school).values('id', 'head')
    return Response(expense_heads)




@api_view(['POST'])
def add_income_expense(request):
    data = request.data
    try:
        head  = models.ChartOfAccount.objects.get(id=data['head'])
    except models.ChartOfAccount.DoesNotExist:
        return Response({"error": "Income or Expense Head does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    date = data['date']
    particulars = data['particulars']
    amount = data['amount']
    school = request.user.school
    
    created = models.IncomeExpense.objects.create(head=head, date=date, particulars=particulars, amount=amount, school=school)

    if created:
        return Response({"message": f"{head.type} created successfully"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": f"Failed to create {head.type}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_income_expenses(request):
    income_expenses = models.IncomeExpense.objects.filter(
        school=request.user.school
    ).select_related('head').order_by('-date')
    
    serializer = serializers.IncomeExpenseSerializer(income_expenses, many=True)
    return Response(serializer.data)





@api_view(['DELETE'])
def delete_income_expense(request, id):
    deleted = models.IncomeExpense.objects.filter(id=id).delete()
    if deleted:
        return Response({"message": "Income or Expense deleted successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to delete Income or Expense"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def get_exam_sessions(request):
    exam_sessions = models.ExamSession.objects.values()
    if not exam_sessions:
        from datetime import datetime
        current_year = datetime.now().year
        another_year = current_year + 1
        models.ExamSession.objects.create(name=f"{current_year}-{another_year}")

    exam_sessions = models.ExamSession.objects.values()


    return Response(exam_sessions)



@api_view(['GET'])
def get_class_subjects(request):

    class_subjects = models.ClassSubject.objects.filter(class_name__school=request.user.school).select_related('class_name','subject').only('id', 'subject__subjectName', 'class_name__className').annotate(
        class_id=F('class_name__id'),
        class_title=F('class_name__className'),
        sub_id=F('id'),
        sub_name=F('subject__subjectName')
    )

    # Initialize a defaultdict to group classes and their subjects
    grouped_data = defaultdict(lambda: {"class": {}, "subjects": []})

    # Iterate through the class_subjects data
    for subject in class_subjects:
        class_id = subject.class_id
        # Ensure the class object is set only once
        if not grouped_data[class_id]["class"]:
            grouped_data[class_id]["class"] = {
                "id": class_id,
                "name": subject.class_title
            }
        # Add subject details to the subjects list
        grouped_data[class_id]["subjects"].append({
            "id": subject.sub_id,
            "name": subject.sub_name
        })

    # Convert the grouped data to a list
    result = list(grouped_data.values())

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
def configure_exam_papers(request):

    serializer = serializers.ConfigureExamPaperSerializer(data=request.data)

    if not serializer.is_valid():
        print("Validation failed. Errors:", serializer.errors)
        return Response({"error": "Failed to configure exam papers"}, status=status.HTTP_400_BAD_REQUEST)

    # serializer.save(school = request.user.school)
    serializer.save(request=request)
    return Response({"message": "Exam papers configured successfully"}, status=status.HTTP_201_CREATED)




@api_view(['GET'])
def get_exams(request, exam_session_id):

    try:
        # print(exam_session_id)
        exam_session = models.ExamSession.objects.get(id=exam_session_id)
        # print(exam_session)
    except models.ExamSession.DoesNotExist:
        return Response({"error": "Exam session does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    exams = models.Exam.objects.filter(school=request.user.school, session=exam_session).values('id','name')
    # print(exams)
    return Response(exams)




@api_view(['DELETE'])
def delete_exam(request, exam_id):
    deleted = models.Exam.objects.filter(id=exam_id).delete()
    if deleted:
        return Response({"message": "Exam deleted successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to delete Exam"}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
def get_exam_papers(request, exam_id):
    exam = models.Exam.objects.select_related('session').get(id=exam_id)
    response = {
        "session":{
            'id': exam.session.id,
            'name': exam.session.name
        },
        "exam_name": exam.name,
        "exam_id": exam.id,
        'start_date': exam.start_date,
        'end_date': exam.end_date,
    }

    exam_papers = models.ExamPaper.objects.filter(exam=exam).select_related('subject', 'subject__class_name').annotate(
        exam_paper_id = F('id'),
        subject_name=F('subject__subject__subjectName'),
        class_id=F('subject__class_name_id'),
        class_name=F('subject__class_name__className'),

    ).values('exam_paper_id', 'subject_name', 'full_marks', 'pass_marks','class_name')



    grouped_as_class_exam_papers = defaultdict(list)

    for paper in exam_papers:
        grouped_as_class_exam_papers[paper['class_name']].append({
            'exam_paper_id': paper['exam_paper_id'],
            'subject_name': paper['subject_name'],
            'total_marks': paper['full_marks'],
            'pass_marks': paper['pass_marks'],
        })

    response['exam_papers'] = grouped_as_class_exam_papers


    # import pprint
    # pprint.pprint(response)
    return Response(response, status=status.HTTP_200_OK)





@api_view(['DELETE'])
def delete_exam_paper(request, paper_id):
    # print(paper_id)
    deleted = models.ExamPaper.objects.filter(id=paper_id).delete()
    if not deleted:
        return Response({"message": "Failed to delete Exam paper"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Exam paper deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def update_exam_papers(request):
    # print(request.data)
    data = request.data
    exam_session_id = data.get('session').get('id')
    session = models.ExamSession.objects.get(id=exam_session_id)
    if not session:
        return Response({"error": "Session does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    

    exam_id = data['exam_id']
    exam = models.Exam.objects.get(id=exam_id)
    if not exam:
        return Response({"error": "Exam does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    models.Exam.objects.filter(id=exam_id).update(
        session = session,
        name = data['exam_name'],
        start_date = data['start_date'],
        end_date = data['end_date'],
    )
    exam_papers = data['exam_papers']

    for classname, papers in exam_papers.items():
        for paper in papers:
            try:
                # print(paper)
                models.ExamPaper.objects.filter(id=paper['exam_paper_id']).update(
                    full_marks = paper['total_marks'],
                    pass_marks = paper['pass_marks'],
                )
            except models.ExamPaper.DoesNotExist:
                return Response({"error": f"Exam paper with id {paper['exam_paper_id']} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": "Exam papers updated successfully"}, status=status.HTTP_201_CREATED)





@api_view(['GET'])
def get_exams_classes(request, exam_id):
    # print(exam_id)
    try:
        exam = models.Exam.objects.get(id=exam_id)
    except models.Exam.DoesNotExist:
        return Response({"error": "Exam does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    classes = models.ExamPaper.objects.filter(exam=exam).annotate(class_name=F('subject__class_name__className'), class_id=F('subject__class_name_id')).values('class_name', 'class_id').distinct()
    # print(classes)
    return Response(classes, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_students_with_marks(request, exam_id, class_id):

    try:
        class_name = models.Class.objects.get(id=class_id)
    except models.Class.DoesNotExist:
        return Response({"error": "Class does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    

    try:
        exam = models.Exam.objects.get(id=exam_id)
    except models.Exam.DoesNotExist:
        return Response({"error": "Exam does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    

    obtained_marks = models.ObtainedMark.objects.filter(student__classOfAdmission=class_name, paper__exam=exam).annotate(
        mark_id = F('id'),
        enr_no = F('student__enrollmentId'),
        student_name=Concat(
            F('student__studentFirstName'),
            Value(' '),
            F('student__studentMiddleName'),
            Value(' '),
            F('student__studentLastName')
        ),
        father_name=Concat(
            F('student__fatherFirstName'),
            Value(' '),
            F('student__fatherMiddleName'),
            Value(' '),
            F('student__fatherLastName')
        ),
        paper_name = F('paper__subject__subject__subjectName'),
    ).values('mark_id', 'enr_no','student_id', 'student_name', 'father_name', 'paper_id', 'paper_name', 'marks').order_by('student_name')


    # print(exam.exam_papers__subject.all())


    # Initialize a defaultdict to group data by student_id
    grouped_data = defaultdict(lambda: {
        'enr_no': None,
        'student_id': None,
        'student_name': '',
        'father_name': '',
        'marks': []
    })


    # Iterate through the obtained marks and group by student_id
    for mark in obtained_marks:
        student_id = mark['student_id']
        
        # Add the basic student info if it's not already added
        if grouped_data[student_id]['student_id'] is None:
            grouped_data[student_id]['student_id'] = student_id
            grouped_data[student_id]['enr_no'] = mark['enr_no']
            grouped_data[student_id]['student_name'] = mark['student_name']
            grouped_data[student_id]['father_name'] = mark['father_name']
        
        # Append the paper data to the exam_papers list
        grouped_data[student_id]['marks'].append({
            'paper_id': mark['paper_id'],
            'paper_name': mark['paper_name'],
            'mark_id': mark['mark_id'],
            'marks': mark['marks']
        })

    # import pprint
    # pprint.pprint()
    response_data = list(grouped_data.values())

    return Response(response_data, status=status.HTTP_200_OK)





@api_view(['GET'])
def get_subjects_for_this_exam(request, exam_id, class_id):
    from .utils import get_subjects_for_exam
    this_class_papers = get_subjects_for_exam(request, exam_id, class_id)
    # print(this_class_papers)
    if not this_class_papers:
        return Response({"error": "No subjects found for this class"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(this_class_papers, status=status.HTTP_200_OK)





@api_view(['GET'])
def get_students_for_marks_entry(request,exam_id, class_id):

    class_name = get_object_or_404(models.Class, id=class_id)

    try:
        students = models.Student.objects.filter(classOfAdmission=class_name)
    except models.Student.DoesNotExist:
        return Response({"message": "Students doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


    exam = get_object_or_404(models.Exam, id=exam_id)

    try:
        exam_papers = models.ExamPaper.objects.filter(exam=exam)
    except models.ExamPaper.DoesNotExist:
        return Response({"message": "Exam Papers doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    for student in students:
        for paper in exam_papers:
            try:
                mark = models.ObtainedMark.objects.get(student=student, paper=paper)
            except models.ObtainedMark.DoesNotExist:
                models.ObtainedMark.objects.create(student=student, paper=paper, marks=0)
                


    obtained_marks = models.ObtainedMark.objects.filter(student__classOfAdmission=class_name, paper__exam=exam).annotate(
        mark_id = F('id'),
        enr_no = F('student__enrollmentId'),
        student_name=Concat(
            F('student__studentFirstName'),
            Value(' '),
            F('student__studentMiddleName'),
            Value(' '),
            F('student__studentLastName')
        ),
        father_name=Concat(
            F('student__fatherFirstName'),
            Value(' '),
            F('student__fatherMiddleName'),
            Value(' '),
            F('student__fatherLastName')
        ),
        paper_name = F('paper__subject__subject__subjectName'),
        paper_full_marks = F('paper__full_marks'),
        paper_pass_marks = F('paper__pass_marks'),

    ).values('mark_id', 'enr_no','student_id', 'student_name', 'father_name', 'paper_id', 'paper_name','paper_full_marks','paper_pass_marks', 'marks').order_by('student_name')


    response = {}

    for mark in obtained_marks:
        if mark['student_id'] not in response:
            response[mark['student_id']] = {
                'student_id':mark['student_id'],
                'enr_no': mark['enr_no'],
                'student_name': mark['student_name'],
                'father_name': mark['father_name'],
                'marks': []
            }
        response[mark['student_id']]['marks'].append({
            'paper_id': mark['paper_id'],
            'paper_name': mark['paper_name'],
            'mark_id': mark['mark_id'],
            'marks': mark['marks'],
            'paper_full_marks': mark['paper_full_marks'],
            'paper_pass_marks': mark['paper_pass_marks'],
        })

    # print(list(response.values()))
    final_response = list(response.values())


    return Response(final_response, status=status.HTTP_200_OK)




@api_view(['POST'])
def update_marks(request):

    # print(request.data)
    # {'student_id': 47, 'enr_no': 'ENR-EE45D3C93C', 'student_name': 'Amanda Troy Gonzalez', 'father_name': 'Christopher Jesse Evans', 'marks': [{'paper_id': 2, 'paper_name': 'Nepali', 'mark_id': 175, 'marks': '10', 'paper_full_marks': 100, 'paper_pass_marks': 40}, {'paper_id': 3, 'paper_name': 'Computer Science', 'mark_id': 176, 'marks': '20', 'paper_full_marks': 50, 'paper_pass_marks': 20}]}

    student = get_object_or_404(models.Student, id=request.data['student_id'])
    for paper in request.data['marks']:
        exam_paper = get_object_or_404(models.ExamPaper, id=paper['paper_id'])

        mark = get_object_or_404(models.ObtainedMark, student=student, paper=exam_paper)
        mark.marks = paper['marks']
        mark.save()


    return Response({"message": "Marks updated successfully"}, status=status.HTTP_200_OK)





@api_view(['GET'])
def get_student_by_enr_no(request,exam_id, class_id, enr_no):

    class_name = get_object_or_404(models.Class, id=class_id)

    try:
        students = models.Student.objects.filter(classOfAdmission=class_name)
    except models.Student.DoesNotExist:
        return Response({"message": "Students doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


    exam = get_object_or_404(models.Exam, id=exam_id)

    try:
        exam_papers = models.ExamPaper.objects.filter(exam=exam)
    except models.ExamPaper.DoesNotExist:
        return Response({"message": "Exam Papers doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    for student in students:
        for paper in exam_papers:
            try:
                mark = models.ObtainedMark.objects.get(student=student, paper=paper)
            except models.ObtainedMark.DoesNotExist:
                models.ObtainedMark.objects.create(student=student, paper=paper, marks=0)
                


    obtained_marks = models.ObtainedMark.objects.filter(student__classOfAdmission=class_name, student__enrollmentId=enr_no, paper__exam=exam).annotate(
        mark_id = F('id'),
        enr_no = F('student__enrollmentId'),
        student_name=Concat(
            F('student__studentFirstName'),
            Value(' '),
            F('student__studentMiddleName'),
            Value(' '),
            F('student__studentLastName')
        ),
        father_name=Concat(
            F('student__fatherFirstName'),
            Value(' '),
            F('student__fatherMiddleName'),
            Value(' '),
            F('student__fatherLastName')
        ),
        paper_name = F('paper__subject__subject__subjectName'),
        paper_full_marks = F('paper__full_marks'),
        paper_pass_marks = F('paper__pass_marks'),

    ).values('mark_id', 'enr_no','student_id', 'student_name', 'father_name', 'paper_id', 'paper_name','paper_full_marks','paper_pass_marks', 'marks').order_by('student_name')


    response = {}

    for mark in obtained_marks:
        if mark['student_id'] not in response:
            response[mark['student_id']] = {
                'student_id':mark['student_id'],
                'enr_no': mark['enr_no'],
                'student_name': mark['student_name'],
                'father_name': mark['father_name'],
                'marks': []
            }
        response[mark['student_id']]['marks'].append({
            'paper_id': mark['paper_id'],
            'paper_name': mark['paper_name'],
            'mark_id': mark['mark_id'],
            'marks': mark['marks'],
            'paper_full_marks': mark['paper_full_marks'],
            'paper_pass_marks': mark['paper_pass_marks'],
        })

    # print(list(response.values()))
    final_response = list(response.values())


    return Response(final_response, status=status.HTTP_200_OK)





@api_view(['GET'])
def get_student_report(request,exam_id, search_key):

    #clean search key by removing leading and trailing spaces
    search_key = search_key.strip()
    try:
        student = models.Student.objects.get(enrollmentId=search_key) #search by enrollment id
    except models.Student.DoesNotExist:
        try:
            student = models.Student.objects.filter(student_full_name__icontains=search_key).first() #search by full name
        except models.Student.DoesNotExist:
            try:
                student = models.Student.objects.filter(student_father_combined_name__icontains=search_key).first() #search by student and father name
            except models.Student.DoesNotExist:
                return Response({"message": "Student doesn't exist"}, status=status.HTTP_400_BAD_REQUEST) 
            


    try:
        exam = models.Exam.objects.get(id=exam_id)
    except models.Exam.DoesNotExist:
        return Response({"message": "Exam doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    
    student_data = {
        'enr_no': student.enrollmentId,
        'student_name': student.student_full_name,
        'father_name': student.father_full_name,
        'class_name': student.classOfAdmission.className,
    }
    obtained_marks = models.ObtainedMark.objects.filter(student=student, paper__exam=exam).annotate(
        paper_name = F('paper__subject__subject__subjectName'),
        paper_full_marks = F('paper__full_marks'),
        paper_pass_marks = F('paper__pass_marks'),
    ).values('paper_name', 'paper_full_marks', 'paper_pass_marks', 'marks').order_by('paper_name')

    response_data = {
        'student_data': student_data,
        'obtained_marks': obtained_marks
    }

    return Response(response_data, status=status.HTTP_200_OK)





@api_view(['GET'])
def get_marks(request,exam_id, class_id):

    class_name = get_object_or_404(models.Class, id=class_id)

    try:
        students = models.Student.objects.filter(classOfAdmission=class_name)
    except models.Student.DoesNotExist:
        return Response({"message": "Students doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


    exam = get_object_or_404(models.Exam, id=exam_id)

    try:
        exam_papers = models.ExamPaper.objects.filter(exam=exam)
    except models.ExamPaper.DoesNotExist:
        return Response({"message": "Exam Papers doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

                
    obtained_marks = models.ObtainedMark.objects.filter(student__classOfAdmission=class_name, paper__exam=exam).annotate(
        mark_id = F('id'),
        enr_no = F('student__enrollmentId'),
        student_name=Concat(
            F('student__studentFirstName'),
            Value(' '),
            F('student__studentMiddleName'),
            Value(' '),
            F('student__studentLastName')
        ),
        father_name=Concat(
            F('student__fatherFirstName'),
            Value(' '),
            F('student__fatherMiddleName'),
            Value(' '),
            F('student__fatherLastName')
        ),
        paper_name = F('paper__subject__subject__subjectName'),
        paper_full_marks = F('paper__full_marks'),
        paper_pass_marks = F('paper__pass_marks'),

    ).values('mark_id', 'enr_no','student_id', 'student_name', 'father_name', 'paper_id', 'paper_name','paper_full_marks','paper_pass_marks', 'marks').order_by('student_name')


    response = {}

    for mark in obtained_marks:
        if mark['student_id'] not in response:
            response[mark['student_id']] = {
                'student_id':mark['student_id'],
                'enr_no': mark['enr_no'],
                'student_name': mark['student_name'],
                'father_name': mark['father_name'],
                'marks': []
            }
        response[mark['student_id']]['marks'].append({
            'paper_id': mark['paper_id'],
            'paper_name': mark['paper_name'],
            'mark_id': mark['mark_id'],
            'marks': mark['marks'],
            'paper_full_marks': mark['paper_full_marks'],
            'paper_pass_marks': mark['paper_pass_marks'],
        })

    # print(list(response.values()))
    final_response = list(response.values())


    return Response(final_response, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_months(request):
    months = models.Month.objects.all()
    return Response(list(months.values()), status=status.HTTP_200_OK)




@api_view(['GET'])
def get_new_receipt_no(request):
    receipt_no = models.Receipt.get_new_receipt_no()
    return Response(receipt_no, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_student_for_receipt(request, enr_no):

    try:
        student = models.Student.objects.annotate(
            Roll_No = F('rollNo'),
            Student_Name = F('student_full_name'),
            Father_Name = F('father_full_name'),
            Class_Name = F('classOfAdmission__className'),
            monthly_fee = F('classOfAdmission__monthlyFees'),
        ).values('id','Student_Name', 'Class_Name',  'Father_Name','Roll_No', 'monthly_fee').get(enrollmentId=enr_no)
    except models.Student.DoesNotExist:
        return Response({"message": "Student doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


    try:
        old_receipts = models.Receipt.objects.filter(student_id=student['id'])
    except models.Receipt.DoesNotExist:
        return Response({"message": "Receipt doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if old_receipts:
            old_fees = float(old_receipts.aggregate(sum_total=Sum('remaining_fees'))['sum_total'])
            months_paid = [ {'id':month.id, 'name':month.name}  for receipt in old_receipts for month in receipt.months.all()]
        else:
            old_fees = 0
            months_paid = []
            
            
    # print(months_paid)


    student['old_fees'] = old_fees
    student['paid_months'] = months_paid

    # print(student)
    return Response(student, status=status.HTTP_200_OK)




@api_view(['POST'])
@transaction.atomic
def create_receipt(request):
    data = request.data

    if not data:
        return Response({"message": "Failed to create receipt"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        student = models.Student.objects.get(id=data.get('student'))
    except models.Student.DoesNotExist:
        return Response({"message": "Student doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    months = data.get('months')
    data = {key: value for key, value in data.items() if key not in ['student', 'months']}
    
    # print(data)
    try:
        old_receipts = models.Receipt.objects.filter(student=student)
    except models.Receipt.DoesNotExist:
        return Response({"message": "Receipt doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # print(old_receipts)
        for receipt in old_receipts:
            if receipt.remaining_fees > 0 and data['deposit_fees'] >= receipt.remaining_fees:
                receipt.remaining_fees = 0
                data['deposit_fees'] -= receipt.remaining_fees
                receipt.save()
        
    
    
    receipt = models.Receipt.objects.create(**data, student=student)

    for month in months:
        receipt.months.add(month)

        
    response = {
        "message": "Receipt created successfully",
        "receipt_no": data.get('receipt_no'),
    }
    return Response(response, status=status.HTTP_201_CREATED)
    
    # print(data)   
    
    # return Response({"message": "Receipt created successfully"}, status=status.HTTP_201_CREATED)





@api_view(['GET'])
def get_receipts(request):

    receipts = models.Receipt.objects.select_related('student').prefetch_related('months').annotate(
        receiptNo=F('receipt_no'),
        studentName=F('student__student_full_name'),
        className=F('student__classOfAdmission__className'),
        enrollmentId=F('student__enrollmentId'),
        date=F('receipt_date'),
        description=F('remarks'),
        remainingFee=F('remaining_fees'),
        paid=F('deposit_fees'),
        netFees=F('net_fees'),
    ).values(
        'id',
        'receiptNo',
        'studentName',
        'className',
        'enrollmentId',
        'date',
        'description',
        'remainingFee',
        'paid',
        'netFees',
        'remarks',
        'months__name'
    ).order_by('-date')

    # Group months by receipt ID
    receipts_dict = {}
    for receipt in receipts:
        receipt_id = receipt['id']
        if receipt_id not in receipts_dict:
            receipts_dict[receipt_id] = {**receipt, 'months': []}
        receipts_dict[receipt_id]['months'].append(receipt['months__name'])

    final_receipts = list(receipts_dict.values())

    return Response(final_receipts, status=status.HTTP_200_OK)




@api_view(['DELETE'])
def delete_receipt(request):
    # print(request.data)
    for receipt_id in request.data:
        try:
            receipt = models.Receipt.objects.get(id=receipt_id)
        except models.Receipt.DoesNotExist:
            return Response({"message": f"Receipt with id {receipt_id} doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        receipt.delete()

    return Response({"message": "Receipt deleted successfully"}, status=status.HTTP_204_NO_CONTENT)





@api_view(['GET'])
def get_students_for_attendance(request, date, class_id):
    from datetime import datetime
    date = datetime.strptime(date, '%Y-%m-%d').date()

    try:
        attendances = models.Attendance.objects.filter(date=date, student__classOfAdmission__id=class_id).annotate(
                    rollNo = F('student_id'),
                    enrollmentId = F('student__enrollmentId'),
                    name = F('student__student_full_name'),
                    fatherName = F('student__father_full_name'),
                    gender = F('student__gender'),

                ).values(
                    'id',
                    'rollNo',
                    'enrollmentId',
                    'name',
                    'fatherName',
                    'gender',
                    'status'
                )    
    except models.Attendance.DoesNotExist:
        return Response({"message": "Attendance doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    if attendances.exists():
        return Response(list(attendances), status=status.HTTP_200_OK)
    

    try:
        students = models.Student.objects.filter(classOfAdmission__id=class_id)
    except models.Class.DoesNotExist:
        return Response({"message": "Class doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    for student in students:
        try:
            models.Attendance.objects.create(
                student=student,
                date=date,
                status=''
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    

    try:    
        attendances = models.Attendance.objects.filter(date=date, student__classOfAdmission__id=class_id).annotate(
            rollNo = F('student_id'),
            enrollmentId = F('student__enrollmentId'),
            name = F('student__student_full_name'),
            fatherName = F('student__father_full_name'),
            gender = F('student__gender'),

        ).values(
            'id',
            'rollNo',
            'enrollmentId',
            'name',
            'fatherName',
            'gender',
            'status'
        )
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


    return Response(list(attendances), status=status.HTTP_200_OK)





@api_view(['POST'])
def update_attendance(request):
    attendances = request.data
    for attendance in attendances:
        try:
            models.Attendance.objects.filter(id=attendance['id']).update(status=attendance['status'])
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    return Response({"message": "Attendance updated successfully"}, status=status.HTTP_200_OK)





@api_view(['GET'])
def get_class_attendance_by_month(request, year, month, class_id):
    
    try:
        attendances = models.Attendance.objects.filter(student__classOfAdmission__id=class_id, date__year=year, date__month=month).annotate(
            rollNo = F('student_id'),
            name = F('student__student_full_name'),
            className = F('student__classOfAdmission__className'),
        ).values(
            'rollNo',
            'name',
            'className',
            'status',
            'date',
         
        ).order_by('date')
    except models.Attendance.DoesNotExist:
        return Response({"message": "Attendance doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    if not attendances.exists():
        return Response({"message": "Attendance doesn't exist for this month"}, status=status.HTTP_404_NOT_FOUND)

    response = {}
    for attendance in attendances:
        roll_no = attendance['rollNo']
        day = attendance['date'].day  # Extract the day from the date

        if roll_no not in response:
            response[roll_no] = {
                "rollNo": roll_no,
                "name": attendance['name'],
                "className": attendance['className'],
                "status": {
                    day: attendance['status']
                },
            }
        else:
            # Add or update the status for the specific day
            response[roll_no]['status'][day] = attendance['status']
       

    
    for rollNo in response:
        response[rollNo]['totalP'] = list(response[rollNo]['status'].values()).count('P')
        response[rollNo]['totalA'] = list(response[rollNo]['status'].values()).count('A')
        response[rollNo]['totalL'] = list(response[rollNo]['status'].values()).count('L')
        


    return Response(list(response.values()), status=status.HTTP_200_OK)



@api_view(['GET'])
def get_class_attendance_by_month_search_term(request, year, month, search_type, search_term):
    if search_type == '' or search_term == '':
        return Response({"message": "Search type and search term are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if search_type == 'name':
            attendances = models.Attendance.objects.filter(student__student_full_name__icontains = search_term, date__year=year, date__month=month)

        elif search_type == 'enrNo':
            attendances = models.Attendance.objects.filter(student__enrollmentId = search_term, date__year=year, date__month=month)
        else:
            return Response({"message": "Invalid search type"}, status=status.HTTP_400_BAD_REQUEST)
        
        attendances = attendances.annotate(
                rollNo = F('student_id'),
                name = F('student__student_full_name'),
                className = F('student__classOfAdmission__className'),
                ).values(
                    'rollNo',
                    'name',
                    'className',
                    'status',
                    'date',
                
                ).order_by('date')

    except models.Attendance.DoesNotExist:
        return Response({"message": "Attendance doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)



    if not attendances.exists():
        return Response({"message": "Attendance doesn't exist for this month"}, status=status.HTTP_404_NOT_FOUND)

    response = {}
    for attendance in attendances:
        roll_no = attendance['rollNo']
        day = attendance['date'].day  # Extract the day from the date

        if roll_no not in response:
            response[roll_no] = {
                "rollNo": roll_no,
                "name": attendance['name'],
                "className": attendance['className'],
                "status": {
                    day: attendance['status']
                },
            }
        else:
            # Add or update the status for the specific day
            response[roll_no]['status'][day] = attendance['status']
       

    
    for rollNo in response:
        response[rollNo]['totalP'] = list(response[rollNo]['status'].values()).count('P')
        response[rollNo]['totalA'] = list(response[rollNo]['status'].values()).count('A')
        response[rollNo]['totalL'] = list(response[rollNo]['status'].values()).count('L')
        


    return Response(list(response.values()), status=status.HTTP_200_OK)
    # return Response("ok", status=status.HTTP_200_OK)




@api_view(['GET'])
def get_employees_for_attendance(request, date):
    from datetime import datetime
    date = datetime.strptime(date, '%Y-%m-%d').date()

    try:
        attendances = models.EmployeeAttendance.objects.filter(date=date).annotate(
                    enrollmentId = F('employee__employeeId'),
                    name = F('employee__employee_full_name'),
                    fatherName = F('employee__father_full_name'),
                    role = F('employee__selectRole'),
                ).values(
                    'id',
                    'enrollmentId',
                    'name',
                    'fatherName',
                    'role',
                    'status'
                )    
    except models.EmployeeAttendance.DoesNotExist:
        return Response({"message": "EmployeeAttendance doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    if attendances.exists():
        return Response(list(attendances), status=status.HTTP_200_OK)
    

    try:
        employees = models.Employee.objects.all()
    except models.Employee.DoesNotExist:
        return Response({"message": "Employee doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    for employee in employees:
        try:
            models.EmployeeAttendance.objects.create(
                employee=employee,
                date=date,
                status=''
            )
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    

    try:    
        attendances = models.EmployeeAttendance.objects.filter(date=date).annotate(
                    enrollmentId = F('employee__employeeId'),
                    name = F('employee__employee_full_name'),
                    fatherName = F('employee__father_full_name'),
                    role = F('employee__selectRole'),
                ).values(
                    'id',
                    'enrollmentId',
                    'name',
                    'fatherName',
                    'role',
                    'status'
                )    
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


    return Response(list(attendances), status=status.HTTP_200_OK)



@api_view(['POST'])
def update_employee_attendance(request):
    attendances = request.data
    for attendance in attendances:
        try:
            models.EmployeeAttendance.objects.filter(id=attendance['id']).update(status=attendance['status'])
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    return Response({"message": "Employee Attendance updated successfully"}, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_employee_attendance_by_month(request, year, month):
    
    try:
        attendances = models.EmployeeAttendance.objects.filter(date__year=year, date__month=month).annotate(
            employeeId = F('employee__employeeId'),
            name = F('employee__employee_full_name'),
            role = F('employee__selectRole'),
        ).values(
            'id',
            'employeeId',
            'name',
            'role',
            'status',
            'date',
         
        ).order_by('date')
    except models.EmployeeAttendance.DoesNotExist:
        return Response({"message": "EmployeeAttendance doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    if not attendances.exists():
        return Response({"message": "Attendance doesn't exist for this month"}, status=status.HTTP_404_NOT_FOUND)

    response = {}
    for attendance in attendances:
        employeeId = attendance['employeeId']
        day = attendance['date'].day  # Extract the day from the date

        if employeeId not in response:
            response[employeeId] = {
                "employeeId": employeeId,
                "name": attendance['name'],
                "role": attendance['role'],
                "status": {
                    day: attendance['status']
                },
            }
        else:
            # Add or update the status for the specific day
            response[employeeId]['status'][day] = attendance['status']
       

    
    for employeeId in response:
        response[employeeId]['totalP'] = list(response[employeeId]['status'].values()).count('P')
        response[employeeId]['totalA'] = list(response[employeeId]['status'].values()).count('A')
        response[employeeId]['totalL'] = list(response[employeeId]['status'].values()).count('L')
        


    return Response(list(response.values()), status=status.HTTP_200_OK)




@api_view(['GET'])
def get_employee_attendance_by_month_search_term(request, year, month, search_type, search_term):
    if search_type == '' or search_term == '':
        return Response({"message": "Search type and search term are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    filters = {
        'date__year': year,
        'date__month': month
    }
    
    if search_type == 'name':
        filters['employee__employee_full_name__icontains'] = search_term
    elif search_type == 'empId':
        filters['employee__employeeId'] = search_term
    else:
        return Response({"message": "Invalid search type"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        attendances = models.EmployeeAttendance.objects.filter(**filters).annotate(
            employeeId=F('employee__employeeId'),
            name=F('employee__employee_full_name'),
            role=F('employee__selectRole'),
        ).values(
            'id',
            'employeeId',
            'name',
            'role',
            'status',
            'date',
        ).order_by('date')
    except models.EmployeeAttendance.DoesNotExist:
        return Response({"message": "Attendance doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)



    if not attendances.exists():
        return Response({"message": "Attendance doesn't exist for this month"}, status=status.HTTP_404_NOT_FOUND)

    response = {}
    for attendance in attendances:
        employeeId = attendance['employeeId']
        day = attendance['date'].day  # Extract the day from the date

        if employeeId not in response:
            response[employeeId] = {
                "employeeId": employeeId,
                "name": attendance['name'],
                "role": attendance['role'],
                "status": {
                    day: attendance['status']
                },
            }
        else:
            # Add or update the status for the specific day
            response[employeeId]['status'][day] = attendance['status']
       

    
    for employeeId in response:
        response[employeeId]['totalP'] = list(response[employeeId]['status'].values()).count('P')
        response[employeeId]['totalA'] = list(response[employeeId]['status'].values()).count('A')
        response[employeeId]['totalL'] = list(response[employeeId]['status'].values()).count('L')
        


    return Response(list(response.values()), status=status.HTTP_200_OK)
    # return Response("ok", status=status.HTTP_200_OK)












