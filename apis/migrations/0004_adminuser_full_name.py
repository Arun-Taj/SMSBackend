# Generated by Django 5.1.1 on 2024-10-02 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_remove_adminuser_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
