# Generated by Django 3.1.2 on 2021-02-27 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compliance_digitalization_app', '0007_newdirinline_proof_of_compliance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newdirectivecirculation',
            name='directive_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='newdirinline',
            name='current_status',
            field=models.CharField(blank=True, choices=[('1', 'Pending'), ('2', 'Complete')], max_length=120, null=True),
        ),
    ]
