# Generated by Django 5.1.5 on 2025-02-20 07:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0019_alter_surveypage_options_alter_surveypage_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='surveys.surveypage'),
        ),
    ]
