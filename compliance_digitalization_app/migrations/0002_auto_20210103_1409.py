# Generated by Django 3.1.4 on 2021-01-03 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compliance_digitalization_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newdirectivecirculationinlineinformation',
            name='escalation_notification',
            field=models.CharField(choices=[('1', 'Yes'), ('2', 'No')], max_length=120, null=True),
        ),
    ]