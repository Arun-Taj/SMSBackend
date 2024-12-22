from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from datetime import datetime


class AdminUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        """
        Creates and saves a user with the given username and password.
        """
        if not username:
            raise ValueError("The Username field must be set")
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True)
    dob = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='images/photos/', blank=True, null=True)
    aadhar_no = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True, null=True)
    town_village_city = models.TextField(blank=True, null=True)
    district = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    passport_photo = models.ImageField(upload_to='images/passport_photos/', blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    alt_phone_number = models.CharField(max_length=50, blank=True, null=True)
    
    
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)



    objects = AdminUserManager()

    USERNAME_FIELD = 'username'  # Retain the username field for authentication
    # REQUIRED_FIELDS = []  


    def __str__(self):
        return self.username




class School(models.Model):
    admin = models.OneToOneField(AdminUser, on_delete=models.CASCADE, null=True, related_name='school')
    school_name = models.CharField(max_length=150, null=True, blank=True)
    photo = models.ImageField(upload_to='images/schools/', blank=True, null=True)
    tag_line = models.CharField(max_length=150, blank=True, null=True)
    school_board = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    town_village_city = models.TextField(blank=True, null=True)
    district = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=50, blank=True)


    def __str__(self) -> str:
        return self.admin.username + " - " + self.tag_line



class Employee(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='employees')
    employeeFirstName = models.CharField(max_length=50, null=True, blank=True)
    employeeMiddleName = models.CharField(max_length=50, null=True, blank=True)
    employeeLastName = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    photoUpload = models.ImageField(upload_to='images/employees/', blank=True, null=True)
    aadharNumber = models.CharField(max_length=15, null=True, blank=True)
    phoneNumber = models.CharField(max_length=10, null=True, blank=True)
    alternatePhoneNumber = models.CharField(max_length=10, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    selectRole = models.CharField(max_length=50, null=True, blank=True)
    fatherFirstName = models.CharField(max_length=50, null=True, blank=True)
    fatherMiddleName = models.CharField(max_length=50, null=True, blank=True)
    fatherLastName = models.CharField(max_length=50, null=True, blank=True)
    husbandFirstName = models.CharField(max_length=50, null=True, blank=True)
    husbandMiddleName = models.CharField(max_length=50, null=True, blank=True)
    husbandLastName = models.CharField(max_length=50, null=True, blank=True)
    address1 = models.CharField(max_length=50, null=True, blank=True)
    townVillageCity = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    zipCode = models.CharField(max_length=50, null=True, blank=True)
    currentAddress1 = models.CharField(max_length=50, null=True, blank=True)
    currentTownVillageCity = models.CharField(max_length=50, null=True, blank=True)
    currentDistrict = models.CharField(max_length=50, null=True, blank=True)
    currentState = models.CharField(max_length=50, null=True, blank=True)
    currentCountry = models.CharField(max_length=50, null=True, blank=True)
    currentZipCode = models.CharField(max_length=50, null=True, blank=True)
    sameAsPermanentAddress = models.BooleanField(default=False)
    dateOfJoining = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    caste = models.CharField(max_length=50, null=True, blank=True)
    bloodGroup = models.CharField(max_length=50, null=True, blank=True)
    bioData = models.FileField(upload_to='documents/employees/', blank=True, null=True)
    educationDetails = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)
    mainSubject = models.CharField(max_length=50, null=True, blank=True)
    complementarySubject = models.CharField(max_length=50, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    employeeId = models.CharField(max_length=20, unique=True, editable=False)


    def save(self, *args, **kwargs):
        if not self.employeeId:
            # Generate a unique employeeId based on UUID
            self.employeeId = f'EMP-{uuid.uuid4().hex[:10].upper()}'
        
        super(Employee, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.employeeFirstName} {self.employeeMiddleName} {self.employeeLastName}"
    

    @property
    def full_name(self):
        return f"{self.employeeFirstName} {self.employeeMiddleName} {self.employeeLastName}"
    

 


class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    className = models.CharField(max_length=50, null=True, blank=True, unique=True)
    class_teacher = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    monthlyFees = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('school', 'className')
        verbose_name_plural = 'Classes'


    def __str__(self) -> str:
        return f"{self.className}- {self.school}"







class Student(models.Model):
    rollNo = models.IntegerField(null=True, blank=True, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    aadharNumber = models.CharField(max_length=15, null=True, blank=True)
    alternatePhoneNumber = models.CharField(max_length=10, null=True, blank=True)
    bloodGroup = models.CharField(max_length=10, null=True, blank=True)
    cAddress1 = models.CharField(max_length=100, null=True, blank=True)
    caste = models.CharField(max_length=50, null=True, blank=True)
    ccountry = models.CharField(max_length=50, null=True, blank=True)
    cdistrict = models.CharField(max_length=50, null=True, blank=True)
    classOfAdmission = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='students')
    cstate = models.CharField(max_length=50, null=True, blank=True)
    ctownVillageCity = models.CharField(max_length=50, null=True, blank=True)
    czipCode = models.CharField(max_length=30, null=True, blank=True)
    dateOfBirth = models.DateField(null=True, blank=True)
    disease = models.CharField(max_length=50, null=True, blank=True)
    fatherAadharNumber = models.CharField(max_length=15, null=True, blank=True)
    fatherFirstName = models.CharField(max_length=50, null=True, blank=True)
    fatherLastName = models.CharField(max_length=50, null=True, blank=True)
    fatherMiddleName = models.CharField(max_length=50, null=True, blank=True)
    fatherOccupation = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    guardianAadharNumber = models.CharField(max_length=15, null=True, blank=True)
    guardianFirstName = models.CharField(max_length=50, null=True, blank=True)
    guardianLastName = models.CharField(max_length=50, null=True, blank=True)
    guardianMiddleName = models.CharField(max_length=50, null=True, blank=True)
    guardianOccupation = models.CharField(max_length=50, null=True, blank=True)
    guardianPhoneNumber = models.CharField(max_length=10, null=True, blank=True)
    lastAttendance = models.CharField(max_length=50, null=True, blank=True)

    motherAadharNumber = models.CharField(max_length=15, null=True, blank=True)
    motherFirstName = models.CharField(max_length=50, null=True, blank=True)
    motherLastName = models.CharField(max_length=50, null=True, blank=True)
    motherMiddleName = models.CharField(max_length=50, null=True, blank=True)
    motherOccupation = models.CharField(max_length=50, null=True, blank=True)
    motherTongue = models.CharField(max_length=50, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    pAddress1 = models.CharField(max_length=50, null=True, blank=True)
    pcountry = models.CharField(max_length=50, null=True, blank=True)
    pdistrict = models.CharField(max_length=50, null=True, blank=True)
    personalIdentification = models.CharField(max_length=50, null=True, blank=True)
    phoneNumber = models.CharField(max_length=15, null=True, blank=True)
    pstate = models.CharField(max_length=50, null=True, blank=True)
    ptownVillageCity = models.CharField(max_length=50, null=True, blank=True)
    pzipCode = models.CharField(max_length=30, null=True, blank=True)
    relationWithGuardian = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=30, null=True, blank=True)
    remarks = models.CharField(max_length=50, null=True, blank=True)
    sameAsFatherMother = models.BooleanField(default=False)
    sameAsPermanentAddress = models.BooleanField(default=False)
    studentFirstName = models.CharField(max_length=50, null=True, blank=True)
    studentLastName = models.CharField(max_length=50, null=True, blank=True)
    studentMiddleName = models.CharField(max_length=50, null=True, blank=True)
    transferCertificate = models.CharField(max_length=50, null=True, blank=True)
    enrollmentId = models.CharField(max_length=20, unique=True, editable=False)
    student_full_name = models.CharField(max_length=200, null=True, blank=True)
    father_full_name = models.CharField(max_length=200, null=True, blank=True)
    student_father_combined_name = models.CharField(max_length=400, null=True, blank=True)


    def get_new_roll_no(self):
        try:
            last_roll_no = Student.objects.filter(school=self.school, classOfAdmission=self.classOfAdmission).count()
            return last_roll_no + 1
        except Exception as e:
            return None

    def save(self, *args, **kwargs):

        if not self.rollNo:
            try:
                self.rollNo = self.get_new_roll_no()
            except Exception as e:
                self.rollNo = None

        if not self.enrollmentId:
            # Generate a unique enrollmentId based on UUID
            self.enrollmentId = f'ENR-{uuid.uuid4().hex[:10].upper()}'

        self.student_full_name = f"{self.studentFirstName} {self.studentMiddleName} {self.studentLastName}"
        self.father_full_name = f"{self.fatherFirstName} {self.fatherMiddleName} {self.fatherLastName}"
        self.student_father_combined_name = f"{self.student_full_name} {self.father_full_name}"
        
        super(Student, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.studentFirstName} {self.studentMiddleName} {self.studentLastName}"
    







class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    subjectName = models.CharField(max_length=50, null=True, blank=True)
   
    class Meta:
        unique_together = ('school', 'subjectName')


    def __str__(self) -> str:
        return f"{self.subjectName}-> {self.school}"
    




class ClassSubject(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    subject_teacher = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_subjects')


    class Meta:
        unique_together = ('class_name', 'subject')


    def __str__(self) -> str:
        return f"{self.class_name.className} -> {self.subject}"



CHART_OF_ACCOUNT_TYPES = (
    ('income', 'Income'), ('expense', 'Expense')
)

class ChartOfAccountQuerySet(models.QuerySet):
    def expenses(self):
        return self.filter(type='expense')
    
    def incomes(self):
        return self.filter(type='income')

class ChartOfAccount(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='chart_of_accounts')
    head = models.CharField(max_length=100)
    type = models.CharField(choices=CHART_OF_ACCOUNT_TYPES, default='income', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    objects = ChartOfAccountQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.head} -> {self.school}"





class IncomeExpense(models.Model):
    head = models.ForeignKey(ChartOfAccount, on_delete=models.CASCADE, related_name='incomes')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='incomes')
    date = models.DateField(null=True, blank=True)
    particulars = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)


    def __str__(self) -> str:
        return f"{self.head.head} -> {self.school}"
    


class ExamSession(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self) -> str:
        return self.name



class Exam(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='exams')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.school} => {self.session.name}'s -> {self.name}"
    



class ExamPaper(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_papers')
    subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='exam_papers')
    full_marks = models.IntegerField(null=True, blank=True)
    pass_marks = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('exam', 'subject')


    def __str__(self) -> str:   
        return f"{self.exam} -> {self.subject.subject.subjectName}"





class ObtainedMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='obtained_marks')
    paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='obtained_marks')
    marks = models.IntegerField(null=True, blank=True)


    class Meta:
        unique_together = ('student', 'paper')

    def __str__(self) -> str:
        return f"{self.student} -> {self.paper.subject.subject.subjectName}"






class Month(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self) -> str:
        return self.name




class Receipt(models.Model):
    receipt_no = models.CharField(max_length=50, null=True, blank=True, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='receipts')
    created_at = models.DateField()
    months = models.ManyToManyField(Month, related_name='receipts')
    admission_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    monthly_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    registration_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    fines = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    transport_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    old_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    late_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    other_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)

    total_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2) #gross total
    concession_percentage = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2) #discount in percentage
    concession_amount = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2) #total_fees * concession_percentage i.e. total discount

    net_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2) #total_fees - concession_amount i.e. total to be paid
    deposit_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2) #paid amount
    payment_mode = models.CharField(max_length=50, null=True, blank=True)

    remaining_fees = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)

    remarks = models.TextField(null=True, blank=True)

    #auto generate receipt no serially, follow this pattern, like REC-Date-Serial
    @classmethod
    def get_new_receipt_no(cls, *args, **kwargs):
        date = datetime.now().strftime("%Y-%m-%d")
        serial = cls.objects.count() + 1
        receipt_no = f"{date}{serial}".replace('-', '')
        return f"REC-{receipt_no}"









