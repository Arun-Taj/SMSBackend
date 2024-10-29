from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


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
    



class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    aadharNumber = models.CharField(max_length=15, null=True, blank=True)
    alternatePhoneNumber = models.CharField(max_length=10, null=True, blank=True)
    bloodGroup = models.CharField(max_length=10, null=True, blank=True)
    cAddress1 = models.CharField(max_length=100, null=True, blank=True)
    caste = models.CharField(max_length=50, null=True, blank=True)
    ccountry = models.CharField(max_length=50, null=True, blank=True)
    cdistrict = models.CharField(max_length=50, null=True, blank=True)
    classOfAdmission = models.CharField(max_length=50, null=True, blank=True)
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

    def save(self, *args, **kwargs):


        if not self.enrollmentId:
            # Generate a unique enrollmentId based on UUID
            self.enrollmentId = f'ENR-{uuid.uuid4().hex[:10].upper()}'
        
        super(Student, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.studentFirstName} {self.studentMiddleName} {self.studentLastName}"



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