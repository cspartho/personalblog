# Generated by Django 3.2 on 2021-04-19 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_commment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commment',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]