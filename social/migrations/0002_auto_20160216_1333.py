# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.CharField(max_length=140, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='country',
            field=models.CharField(max_length=140, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='picture',
            field=models.ImageField(null=True, upload_to=b'image/profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='workplace',
            field=models.CharField(max_length=140, null=True),
            preserve_default=True,
        ),
    ]
