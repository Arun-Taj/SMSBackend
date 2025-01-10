import random
from faker import Faker
from django.core.management.base import BaseCommand
from apis.models import ChartOfAccount, School, CHART_OF_ACCOUNT_TYPES

class Command(BaseCommand):
    help = "Populate the IncomeExpense model with fake data"

    def handle(self, *args, **kwargs):
        fake = Faker()
        schools = School.objects.all()

        
        for _ in range(100):  # Number of records to create
            school = schools[0]

            ChartOfAccount.objects.create(
                school=school,
                head=fake.company(),
                type=random.choice(CHART_OF_ACCOUNT_TYPES),
                created_at=fake.date_time_this_year(),
            )

        self.stdout.write(self.style.SUCCESS("Successfully populated Chart of Account with fake data!"))






