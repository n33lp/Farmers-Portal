# Generated by Django 4.2.1 on 2023-05-30 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_rename_employee_name_uploadeddata_employee_first_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploadeddata',
            old_name='employee_first_name',
            new_name='ename',
        ),
    ]