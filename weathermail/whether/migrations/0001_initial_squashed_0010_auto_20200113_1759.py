# Generated by Django 3.0 on 2020-01-14 08:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('whether', '0001_initial'), ('whether', '0002_auto_20200111_1334'), ('whether', '0003_auto_20200111_1600'), ('whether', '0004_auto_20200112_1301'), ('whether', '0005_auto_20200112_1312'), ('whether', '0006_auto_20200112_1317'), ('whether', '0007_auto_20200113_1616'), ('whether', '0008_auto_20200113_1645'), ('whether', '0009_auto_20200113_1649'), ('whether', '0010_auto_20200113_1759')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('created_ts', models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)),
                ('updated_ts', models.DateTimeField(auto_now=True)),
                ('population', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['-population'],
                'unique_together': {('city', 'state')},
            },
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='whether.Location')),
                ('created_ts', models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)),
                ('updated_ts', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature_today', models.IntegerField(blank=True, null=True)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='whether.Location')),
                ('created_ts', models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)),
                ('updated_ts', models.DateTimeField(auto_now=True)),
                ('weather_code', models.PositiveIntegerField(blank=True, null=True)),
                ('weather_description', models.TextField(blank=True, null=True)),
                ('weather_icon', models.CharField(blank=True, max_length=6, null=True)),
                ('temperature_tomorrow', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
