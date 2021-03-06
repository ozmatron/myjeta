# Generated by Django 2.0.6 on 2018-08-17 12:36

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BankHolidays',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=10)),
                ('date', models.CharField(max_length=15)),
                ('holiday', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Bank Holidays',
            },
        ),
        migrations.CreateModel(
            name='Coefficients',
            fields=[
                ('segment', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('intercept', models.FloatField(null=True)),
                ('arrivaltime', models.FloatField(null=True)),
                ('rain', models.FloatField(null=True)),
                ('holiday', models.FloatField(null=True)),
                ('fri', models.FloatField(null=True)),
                ('mon', models.FloatField(null=True)),
                ('sat', models.FloatField(null=True)),
                ('sun', models.FloatField(null=True)),
                ('thu', models.FloatField(null=True)),
                ('tue', models.FloatField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Coefficients',
            },
        ),
        migrations.CreateModel(
            name='Fares',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop', models.IntegerField(null=True)),
                ('route', models.CharField(max_length=10)),
                ('direction', models.IntegerField(null=True)),
                ('stage', models.IntegerField(null=True)),
                ('pattern_id', models.CharField(max_length=10)),
                ('seq', models.IntegerField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Fares',
            },
        ),
        migrations.CreateModel(
            name='Lines',
            fields=[
                ('lineid', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('routes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), size=None)),
            ],
            options={
                'verbose_name_plural': 'Lines',
            },
        ),
        migrations.CreateModel(
            name='Linked',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_name', models.TextField(null=True)),
                ('linked', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), size=None)),
            ],
            options={
                'verbose_name_plural': 'Linked Stops',
            },
        ),
        migrations.CreateModel(
            name='Routes',
            fields=[
                ('routeid', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('lineid', models.CharField(max_length=5, null=True)),
                ('direction', models.IntegerField(null=True)),
                ('stopids', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), size=None)),
            ],
            options={
                'verbose_name_plural': 'Routes',
            },
        ),
        migrations.CreateModel(
            name='Stops',
            fields=[
                ('stopid', models.IntegerField(primary_key=True, serialize=False)),
                ('address', models.TextField()),
                ('lat', models.DecimalField(decimal_places=8, max_digits=10)),
                ('lng', models.DecimalField(decimal_places=8, max_digits=10)),
                ('lines', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), size=None)),
            ],
            options={
                'verbose_name_plural': 'Stops',
            },
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stopid', models.IntegerField(null=True)),
                ('lineid', models.CharField(max_length=10)),
                ('dayofservice', models.CharField(max_length=10)),
                ('destination', models.CharField(max_length=50, null=True)),
                ('schedule', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5), size=None)),
            ],
            options={
                'verbose_name_plural': 'Time Table',
            },
        ),
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=12)),
                ('time', models.CharField(max_length=5, null=True)),
                ('irain', models.IntegerField(null=True)),
                ('rain', models.CharField(max_length=10, null=True)),
                ('itemp', models.IntegerField(null=True)),
                ('temp', models.CharField(max_length=10, null=True)),
                ('iwetb', models.IntegerField(null=True)),
                ('wetb', models.CharField(max_length=10, null=True)),
                ('dewpt', models.CharField(max_length=10, null=True)),
                ('vappr', models.CharField(max_length=10, null=True)),
                ('rhum', models.CharField(max_length=10, null=True)),
                ('msl', models.CharField(max_length=10, null=True)),
            ],
            options={
                'verbose_name_plural': 'Weather',
            },
        ),
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['rain'], name='main_weathe_rain_f14ef7_idx'),
        ),
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['date'], name='main_weathe_date_ab6e08_idx'),
        ),
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['time'], name='main_weathe_time_8c35c1_idx'),
        ),
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['date', 'time'], name='main_weathe_date_965487_idx'),
        ),
        migrations.AddIndex(
            model_name='timetable',
            index=models.Index(fields=['stopid'], name='main_timeta_stopid_0db765_idx'),
        ),
        migrations.AddIndex(
            model_name='timetable',
            index=models.Index(fields=['lineid'], name='main_timeta_lineid_6b855b_idx'),
        ),
        migrations.AddIndex(
            model_name='timetable',
            index=models.Index(fields=['dayofservice'], name='main_timeta_dayofse_481390_idx'),
        ),
        migrations.AddIndex(
            model_name='timetable',
            index=models.Index(fields=['stopid', 'lineid', 'dayofservice', 'destination'], name='main_timeta_stopid_f154f5_idx'),
        ),
        migrations.AddIndex(
            model_name='stops',
            index=models.Index(fields=['stopid'], name='main_stops_stopid_486924_idx'),
        ),
        migrations.AddIndex(
            model_name='routes',
            index=models.Index(fields=['routeid'], name='main_routes_routeid_5b8362_idx'),
        ),
        migrations.AddIndex(
            model_name='linked',
            index=models.Index(fields=['stop_name'], name='main_linked_stop_na_3f3cc5_idx'),
        ),
        migrations.AddIndex(
            model_name='linked',
            index=models.Index(fields=['linked'], name='main_linked_linked_6d05c0_idx'),
        ),
        migrations.AddIndex(
            model_name='lines',
            index=models.Index(fields=['lineid'], name='main_lines_lineid_dad144_idx'),
        ),
        migrations.AddIndex(
            model_name='fares',
            index=models.Index(fields=['stop'], name='main_fares_stop_e66422_idx'),
        ),
        migrations.AddIndex(
            model_name='coefficients',
            index=models.Index(fields=['segment'], name='main_coeffi_segment_32dc18_idx'),
        ),
    ]
