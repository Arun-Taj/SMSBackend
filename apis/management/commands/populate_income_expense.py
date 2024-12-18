import random
from faker import Faker
from django.core.management.base import BaseCommand
from apis.models import IncomeExpense, ChartOfAccount, School, Student, Class

class Command(BaseCommand):
    help = "Populate the IncomeExpense model with fake data"

    def handle(self, *args, **kwargs):
        fake = Faker()
        schools = School.objects.all()
        heads = ChartOfAccount.objects.all()

        if not schools.exists():
            self.stdout.write("No schools found. Add some schools before running this script.")
            return

        if not heads.exists():
            self.stdout.write("No chart of accounts found. Add some heads before running this script.")
            return

        for _ in range(100):  # Number of records to create
            school = random.choice(schools)
            head = random.choice(heads)

            IncomeExpense.objects.create(
                head=head,
                school=school,
                date=fake.date_this_year(),
                particulars=fake.sentence(),
                amount=round(random.uniform(100, 10000), 2),  # Random amount between 100 and 10,000
            )

        self.stdout.write(self.style.SUCCESS("Successfully populated IncomeExpense with fake data!"))






