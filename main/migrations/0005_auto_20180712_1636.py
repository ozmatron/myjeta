# Generated by Django 2.0.6 on 2018-07-12 16:36

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20180709_1318'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coefficients',
            old_name='dayofweek_Friday',
            new_name='fri',
        ),
        migrations.RenameField(
            model_name='coefficients',
            old_name='dayofweek_Monday',
            new_name='mon',
        ),
        migrations.RenameField(
            model_name='coefficients',
            old_name='dayofweek_Saturday',
            new_name='sat',
        ),
        migrations.RenameField(
            model_name='coefficients',
            old_name='dayofweek_Sunday',
            new_name='sun',
        ),
        migrations.RenameField(
            model_name='coefficients',
            old_name='dayofweek_Thursday',
            new_name='thu',
        ),
        migrations.RenameField(
            model_name='coefficients',
            old_name='dayofweek_Tuesday',
            new_name='tue',
        ),
        migrations.AlterField(
            model_name='linked',
            name='linked',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), size=None),
        ),
        migrations.AlterField(
            model_name='stops',
            name='stopid',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
