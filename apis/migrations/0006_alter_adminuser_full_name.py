# Generated by Django 5.1.1 on 2024-10-02 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0005_adminuser_aadhar_no_adminuser_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]