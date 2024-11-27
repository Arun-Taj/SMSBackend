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
# from collections import defaultdict
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
        return super().get_queryset().filter(school=self.request.user.school).order_by('studentFirstName')
    




class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(school=self.request.user.school).order_by('employeeFirstName')
        else:
            raise PermissionError('User is not authenticated')
    

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
            raise PermissionError('User is not authenticated')
        




class SubjectViewSet(viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(school=self.request.user.school)
        else:
            raise PermissionError('User is not authenticated')





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
            raise PermissionError("User is not authenticated")
        

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
    classes = models.Class.objects.annotate(name=F('className')).values('id', 'name')
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















