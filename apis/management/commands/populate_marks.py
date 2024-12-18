from django.core.management.base import BaseCommand
from faker import Faker
import random
from apis.models import Student, ExamPaper, ObtainedMark

class Command(BaseCommand):
    help = "Populate the ObtainedMark model with fake data"

    def handle(self, *args, **kwargs):
        fake = Faker()
        students = list(Student.objects.all())
        papers = list(ExamPaper.objects.all())

        if not students or not papers:
            self.stdout.write(self.style.ERROR("No students or exam papers found!"))
            return

        for _ in range(50):  # Adjust the number of records to create
            student = random.choice(students)
            paper = random.choice(papers)

            # Ensure no duplicate student-paper pairs
            if ObtainedMark.objects.filter(student=student, paper=paper).exists():
                continue

            marks = random.randint(0, 100)  # Assuming marks range from 0 to 100
            ObtainedMark.objects.create(
                student=student,
                paper=paper,
                marks=marks
            )

        self.stdout.write(self.style.SUCCESS("Fake data for ObtainedMark model created successfully!"))
