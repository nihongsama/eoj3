# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-25 22:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problem', '0005_auto_20170825_2201'),
    ]

    operations = [
        migrations.CreateModel(
            name='EditSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('fingerprint', models.CharField(max_length=64)),
                ('last_synchronize', models.DateTimeField(blank=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problem.Problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_synchronize'],
            },
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(1, 'complete'), (0, 'running'), (-1, 'failed')])),
                ('label', models.TextField(blank=True)),
                ('message', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='editsession',
            unique_together=set([('user', 'problem')]),
        ),
    ]