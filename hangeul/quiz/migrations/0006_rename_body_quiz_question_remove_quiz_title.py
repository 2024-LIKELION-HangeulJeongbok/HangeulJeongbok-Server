# Generated by Django 4.2.5 on 2024-11-25 03:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_quiz_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='body',
            new_name='question',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='title',
        ),
    ]
