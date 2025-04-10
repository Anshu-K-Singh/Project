# Generated by Django 5.1.5 on 2025-02-16 16:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('respondent_app', '0003_respondentgroup'),
        ('surveyapp', '0006_supportquery'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HostedSurvey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('external_link', models.URLField()),
                ('company_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('click_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('assigned_groups', models.ManyToManyField(blank=True, to='respondent_app.respondentgroup')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
