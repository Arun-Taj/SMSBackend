import random
from faker import Faker
from django.core.management.base import BaseCommand
from apis.models import School, Employee

class Command(BaseCommand):
    help = "Populate the Employee model with dummy data."

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Fetch or create some related instances
        schools = list(School.objects.all())
        
        if not schools:
            self.stdout.write("Please ensure there are some School and Class entries in the database.")
            return
        
        for _ in range(100):  # Adjust the number of students to create
            school = schools[0]
            
            employee = Employee.objects.create(
                school=school,
                employeeFirstName=fake.first_name(),
                employeeMiddleName=fake.first_name(),
                employeeLastName=fake.last_name(),
            )
                
            
            # Output success message for this student
            self.stdout.write(f"Created Student: {employee.employeeFirstName} {employee.employeeLastName}")