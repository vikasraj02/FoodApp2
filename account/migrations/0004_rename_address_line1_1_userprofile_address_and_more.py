# Generated by Django 5.0 on 2024-01-08 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_user_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='address_line1_1',
            new_name='address',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='address_line1_2',
        ),
    ]
