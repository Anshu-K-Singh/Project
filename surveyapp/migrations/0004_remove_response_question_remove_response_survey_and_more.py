# Generated by Django 5.0 on 2025-01-31 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveyapp', '0003_remove_surveyresponse_survey_alter_question_choices_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='response',
            name='question',
        ),
        migrations.RemoveField(
            model_name='response',
            name='survey',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Response',
        ),
        migrations.DeleteModel(
            name='Survey',
        ),
    ]
