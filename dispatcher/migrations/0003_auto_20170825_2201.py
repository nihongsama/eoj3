# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-25 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatcher', '0002_auto_20170419_0014'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='serverproblemstatus',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='serverproblemstatus',
            name='problem',
        ),
        migrations.RemoveField(
            model_name='serverproblemstatus',
            name='server',
        ),
        migrations.RemoveField(
            model_name='server',
            name='problems',
        ),
        migrations.AddField(
            model_name='server',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='server',
            name='last_synchronize_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.DeleteModel(
            name='ServerProblemStatus',
        ),
    ]
