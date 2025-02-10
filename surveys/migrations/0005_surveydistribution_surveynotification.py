# Generated by Django 5.1.5 on 2025-02-06 10:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('respondent_app', '0003_respondentgroup'),
        ('surveys', '0004_response_user_alter_response_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyDistribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey_distributions', to='respondent_app.respondentgroup')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributions', to='surveys.survey')),
            ],
            options={
                'verbose_name_plural': 'Survey Distributions',
            },
        ),
        migrations.CreateModel(
            name='SurveyNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='surveys.survey')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'survey')},
            },
        ),
    ]
