# Generated by Django 3.0 on 2020-01-15 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whether', '0001_initial_squashed_0010_auto_20200113_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='created_ts',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='created_ts',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='created_ts',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
