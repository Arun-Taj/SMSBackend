from rest_framework import serializers
from .models import *
from PIL import Image
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom user data
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            # 'email': self.user.email,
            # Add any other fields you want
        }
        # Remove the refresh token from the response data
        return data

class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)  # Only for writing, not reading
    photo = serializers.ImageField(required=False, allow_null=True)
    passport_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = AdminUser
        fields = ['id', 'url','username', 'full_name', 'password','gender', 'dob','photo', 'aadhar_no', 'address', 'town_village_city', 'district', 'state', 'country', 'pincode', 'nationality', 'religion', 'passport_photo', 'phone_number', 'alt_phone_number']

    def create(self, validated_data):
        # Create a new user and set the password securely
        user = AdminUser.objects.create(
            username=validated_data['username'],
            full_name=validated_data.get('full_name', ''),
            gender=validated_data.get('gender', ''),
            dob=validated_data.get('dob', ''),
            photo=validated_data.get('photo', ''),
            aadhar_no=validated_data.get('aadhar_no', ''),
            address=validated_data.get('address', ''),
            town_village_city=validated_data.get('town_village_city', ''),
            district=validated_data.get('district', ''),
            state=validated_data.get('state', ''),
            country=validated_data.get('country', ''),
            pincode=validated_data.get('pincode', ''),
            nationality=validated_data.get('nationality', ''),
            religion=validated_data.get('religion', ''),
            passport_photo=validated_data.get('passport_photo', ''),
            phone_number=validated_data.get('phone_number', ''),
            alt_phone_number=validated_data.get('alt_phone_number', ''),
        )
        user.set_password(validated_data['password'])  # Set the password securely
        user.save()
        return user
    

    def validate_photo(self, value):
        """Validate the uploaded image"""
        try:
            img = Image.open(value)
            img.verify()
        except (IOError, SyntaxError):
            raise serializers.ValidationError("Invalid image file")
        return value
    

    def validate_passport_photo(self, value):
        """Validate the uploaded image"""
        try:
            img = Image.open(value)
            img.verify()
        except (IOError, SyntaxError):
            raise serializers.ValidationError("Invalid image file")
        return value
    

    def update(self, instance, validated_data):
        # Check if the password is being updated
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    


class UpdateAdminUserSerializer(AdminUserSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Only for writing, not reading
    username = serializers.CharField(write_only=True, required=False)  # Only for writing, not reading




class SchoolSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = School
        fields = '__all__'







class StudentSerializer(serializers.HyperlinkedModelSerializer):
    # rollNo = serializers.IntegerField(read_only=True)  # Add rollNo as a read-only field
    id = serializers.IntegerField(read_only=True)
    # classOfAdmission = serializers.PrimaryKeyRelatedField() #need to change



    class Meta:
        model = Student
        fields = '__all__'



    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # representation['rollNo'] = self.context.get('rollNo', None)  # Use context if needed
        representation['id'] = instance.id  # or representation['id'] = instance.pk for primary key
        return representation



    def save(self, *args, **kwargs):
        request = self.context.get("request")  # Get request from context
      
        if request:
            # If this is a new instance, set the school
            if self.instance is None:
                self.validated_data['school'] = request.user.school
            else:
                # Only set the school if the instance already exists
                if not self.instance.school:
                    self.instance.school = request.user.school
        super().save(*args, **kwargs)







class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'


    def create(self, validated_data):
        # Assign the authenticated user's school to the employee on creation
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data['school'] = request.user.school
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Avoid overwriting the school field on updates
        validated_data.pop('school', None)
        return super().update(instance, validated_data)
    






class ClassSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    class_teacher_fullname = serializers.CharField(source='class_teacher.full_name', read_only=True)

    class Meta:
        model = Class
        fields = '__all__'


    def create(self, validated_data):
        validated_data['school'] = self.context['request'].user.school  
        return super().create(validated_data)






class SubjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    school = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'



    def create(self, validated_data):
        validated_data['school'] = self.context['request'].user.school  
        return super().create(validated_data)



class SimpleEmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    class Meta:
        model = Employee
        fields = ['id', 'full_name']


# class ClassSubjectSerializer(serializers.ModelSerializer):
#     class_name = ClassSerializer()  # Nested serializer for Class
#     subject = SubjectSerializer()  # Nested serializer for Subject
#     subject_teacher = SimpleEmployeeSerializer()  # Nested serializer for Employee

#     class Meta:
#         model = ClassSubject
#         fields = ['id', 'class_name', 'subject', 'subject_teacher']

class ClassSubjectSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()  # Replace nested serializer
    subject = serializers.SerializerMethodField()  # Replace nested serializer
    subject_teacher = serializers.SerializerMethodField()  # Replace nested serializer

    class Meta:
        model = ClassSubject
        fields = ['id', 'class_name', 'subject', 'subject_teacher']

    def get_class_name(self, obj):
        return {
            "id": obj.class_name.id,
            "name": obj.class_name.name,
            # Add other required fields here
        }

    def get_subject(self, obj):
        return {
            "id": obj.subject.id,
            "name": obj.subject.name,
            # Add other required fields here
        }

    def get_subject_teacher(self, obj):
        return {
            "id": obj.subject_teacher.id,
            "full_name": obj.subject_teacher.full_name,
            # Add other required fields here
        }





class GETClassSubjectSerializer(serializers.ModelSerializer):
    class_name = ClassSerializer()  # Use nested serializer for class_name
    subject = SubjectSerializer()  # Use nested serializer for subject
    subject_teacher = SimpleEmployeeSerializer()  # Use nested serializer for subject_teacher

    class Meta:
        model = ClassSubject
        fields = ['id', 'class_name', 'subject', 'subject_teacher']  # 





class SimpleEmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    class Meta:
        model = Employee
        fields = ['id', 'full_name']




class SubjectSerializerForConfig(serializers.Serializer):
    subjectId = serializers.CharField(max_length=50)  # Adjust max_length as needed
    teacherId = serializers.CharField(max_length=50)  # Adjust max_length as needed



class ClassSubjectSerializerForConfig(serializers.Serializer):
    class_id = serializers.IntegerField()
    subjects = SubjectSerializerForConfig(many=True)  # Assuming SubjectSerializerForConfig is defined elsewhere

    def create(self, validated_data):
        subjects_data = validated_data.pop('subjects')
        try:
            class_instance = Class.objects.get(id=validated_data['class_id'])
        except Class.DoesNotExist:
            raise serializers.ValidationError({"class_id": "Class does not exist."})

        class_subjects = []

        for subject_data in subjects_data:
            try:
                subject_instance = Subject.objects.get(id=subject_data['subjectId'])
            except Subject.DoesNotExist:
                raise serializers.ValidationError({"subjectId": "Subject does not exist."})

            try:
                teacher_instance = Employee.objects.get(id=subject_data['teacherId'])
            except Employee.DoesNotExist:
                raise serializers.ValidationError({"teacherId": "Teacher does not exist."})

            # Check for existing subject in class
            if ClassSubject.objects.filter(class_name=class_instance, subject=subject_instance).exists():
                raise serializers.ValidationError(
                    f"Subject {subject_instance.subjectName} already exists in {class_instance.className}."
                )

            # Create or get ClassSubject
            class_subject, created = ClassSubject.objects.get_or_create(
                class_name=class_instance,
                subject=subject_instance,
                subject_teacher=teacher_instance
            )
            if created:
                class_subjects.append(class_subject)  # Only append newly created instances

        return class_subjects




class IncomeExpenseSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.head')  # Fetch the `head` field from `ChartOfAccount`
    head_type = serializers.CharField(source='head.type')  # Fetch the `type` field from `ChartOfAccount`

    class Meta:
        model = IncomeExpense
        fields = ['id', 'head', 'head_name', 'head_type', 'school', 'date', 'particulars', 'amount']





class ExamSubjectSerializer(serializers.Serializer):
    subjectId = serializers.IntegerField()
    totalMarks = serializers.IntegerField()
    passMarks = serializers.IntegerField()



class ExamClassSerializer(serializers.Serializer):
    classId = serializers.IntegerField()
    subjects = ExamSubjectSerializer(many=True)



class ConfigureExamPaperSerializer(serializers.Serializer):
    currentSession = serializers.IntegerField()
    currentSessionName = serializers.CharField(max_length=255)
    startingDate = serializers.DateField(required=False, allow_null=True)
    endingDate = serializers.DateField(required=False, allow_null=True)
    examName = serializers.CharField(max_length=255)
    classes = ExamClassSerializer(many=True)


    


    def save(self,**kwargs):
        print(self.validated_data)
        data = self.validated_data
        session_id = data.get('currentSession')
        session_instance = ExamSession.objects.get(id=session_id)
        school = kwargs.get('request').user.school
        exam_start_date = data.get('startingDate')
        exam_end_date = data.get('endingDate')
        exam_name = data.get('examName')
        exam = Exam.objects.create(session=session_instance, school=school, name=exam_name, start_date=exam_start_date, end_date=exam_end_date)

        if exam is None:
            return None
        
        classes = data.get('classes')
        for cls in classes:
            subjects = cls.get('subjects')
            for subject in subjects:
                subject_id = subject.get('subjectId')
                total_marks = subject.get('totalMarks')
                pass_marks = subject.get('passMarks')
                subject_instance = ClassSubject.objects.get(id=subject_id)
                print(subject_id, total_marks, pass_marks, subject_instance)
                ExamPaper.objects.create(exam=exam, subject=subject_instance, full_marks=total_marks, pass_marks=pass_marks)
        # return self.validated_data


























