# Generated by Django 3.1.4 on 2021-01-20 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compliance_digitalization_app', '0006_merge_20210120_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='newdirinline',
            name='proof_of_compliance',
            field=models.FileField(blank=True, null=True, upload_to='%Y/%m/%d'),
        ),
    ]