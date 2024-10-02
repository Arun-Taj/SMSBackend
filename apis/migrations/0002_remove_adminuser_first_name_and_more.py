# Generated by Django 5.1.1 on 2024-10-02 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adminuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='last_name',
        ),
        migrations.AddField(
            model_name='adminuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
