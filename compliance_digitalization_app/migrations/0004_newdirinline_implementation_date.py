# Generated by Django 3.1.2 on 2021-01-20 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compliance_digitalization_app', '0003_auto_20210112_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='newdirinline',
            name='implementation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
