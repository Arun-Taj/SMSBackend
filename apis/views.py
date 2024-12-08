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

from django.db.models import F
# from django.contrib.postgres.aggregates import ArrayAgg
from collections import defaultdict
from rest_framework.exceptions import ValidationError





# class CustomTokenBlacklistView(APIView):
#     def post(self, request, *args, **kwargs):
#         refresh_token = request.data.get('refresh')
#         print("refresh",refresh_token)

#         if not refresh_token:
#             return JsonResponse({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Check if the token is in outstanding tokens
#             outstanding_token = OutstandingToken.objects.get(token=refresh_token)
#             print("outstanding",outstanding_token)



#             # Check if it's already blacklisted
#             if not BlacklistedToken.objects.filter(token=outstanding_token).exists():
#                 # Create a new blacklist entry
#                 BlacklistedToken.objects.create(token=outstanding_token)
#                 return JsonResponse({'detail': 'Token blacklisted successfully.'}, status=status.HTTP_205_RESET_CONTENT)
#             else:
#                 return JsonResponse({'detail': 'Token is already blacklisted.'}, status=status.HTTP_200_OK)

#         except OutstandingToken.DoesNotExist:
#             return JsonResponse({'detail': 'Outstanding token does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return JsonResponse({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    




class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(school=self.request.user.school).order_by('employeeFirstName')
        else:
            # raise PermissionError('User is not authenticated')
            return models.Employee.objects.none()
    

    def create(self, request, *args, **kwargs):
        # print("creating, viewset")
        # Manually handle creation to catch validation errors
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # Log validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)



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
    serializer = serializers.ClassSubjectSerializerForConfig(data=data)
    
    if serializer.is_valid():
        try:
            saved_data = serializer.save()
        except ValidationError as e:
            # Extract error details
            error_details = e.detail if hasattr(e, 'detail') else str(e)
            print(error_details)
            return Response({"error": error_details}, status=status.HTTP_400_BAD_REQUEST)
        
        # Serialize saved data for response
        class_subject_serializer = serializers.ClassSubjectSerializer(saved_data, many=True)
        return Response(class_subject_serializer.data, status=status.HTTP_201_CREATED)
    else:
        # Return validation errors from serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





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
        exam_session = models.ExamSession.objects.get(id=exam_session_id)
    except models.ExamSession.DoesNotExist:
        return Response({"error": "Exam session does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    exams = models.Exam.objects.filter(school=request.user.school, session=exam_session).values('id','name')
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











