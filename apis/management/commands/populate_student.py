import random
from faker import Faker
from django.core.management.base import BaseCommand
from apis.models import School, Student, Class

class Command(BaseCommand):
    help = "Populate the Student model with dummy data."

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Fetch or create some related instances
        schools = list(School.objects.all())
        classes = list(Class.objects.all())
        
        if not schools or not classes:
            self.stdout.write("Please ensure there are some School and Class entries in the database.")
            return
        
        for _ in range(100):  # Adjust the number of students to create
            school = random.choice(schools)
            class_of_admission = random.choice(classes)
            
            student = Student.objects.create(
                school=school,
                aadharNumber=fake.random_number(digits=12, fix_len=True),
                alternatePhoneNumber=fake.phone_number()[:10],
                bloodGroup=random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']),
                cAddress1=fake.address(),
                caste=fake.word(),
                ccountry=fake.country(),
                cdistrict=fake.city(),
                classOfAdmission=class_of_admission,
                cstate=fake.state(),
                ctownVillageCity=fake.city(),
                czipCode=fake.postcode(),
                dateOfBirth=fake.date_of_birth(minimum_age=5, maximum_age=18),
                disease=random.choice(['None', 'Asthma', 'Diabetes']),
                fatherAadharNumber=fake.random_number(digits=12, fix_len=True),
                fatherFirstName=fake.first_name_male(),
                fatherLastName=fake.last_name(),
                fatherMiddleName=fake.first_name_male(),
                fatherOccupation=fake.job(),
                gender=random.choice(['Male', 'Female', 'Other']),
                guardianAadharNumber=fake.random_number(digits=12, fix_len=True),
                guardianFirstName=fake.first_name(),
                guardianLastName=fake.last_name(),
                guardianMiddleName=fake.first_name(),
                guardianOccupation=fake.job(),
                guardianPhoneNumber=fake.phone_number()[:10],
                lastAttendance=fake.date_this_year(),
                motherAadharNumber=fake.random_number(digits=12, fix_len=True),
                motherFirstName=fake.first_name_female(),
                motherLastName=fake.last_name(),
                motherMiddleName=fake.first_name_female(),
                motherOccupation=fake.job(),
                motherTongue=fake.language_name(),
                nationality=fake.country(),
                pAddress1=fake.address(),
                pcountry=fake.country(),
                pdistrict=fake.city(),
                personalIdentification=fake.text(max_nb_chars=20),
                phoneNumber=fake.phone_number()[:15],
                pstate=fake.state(),
                ptownVillageCity=fake.city(),
                pzipCode=fake.postcode(),
                relationWithGuardian=random.choice(['Father', 'Mother', 'Uncle', 'Aunt', 'Grandparent']),
                religion=random.choice(['Hinduism', 'Islam', 'Christianity', 'Sikhism', 'Other']),
                remarks=fake.sentence(),
                sameAsFatherMother=random.choice([True, False]),
                sameAsPermanentAddress=random.choice([True, False]),
                studentFirstName=fake.first_name(),
                studentLastName=fake.last_name(),
                studentMiddleName=fake.first_name(),
                transferCertificate=random.choice(['None', 'Available']),
            )
            
            # Output success message for this student
            self.stdout.write(f"Created Student: {student.studentFirstName} {student.studentLastName}")