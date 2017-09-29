# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('username', models.CharField(primary_key=True, max_length=16, serialize=False)),
                ('password', models.CharField(max_length=16)),
                ('following', models.ManyToManyField(to='social.Member')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('pm', models.BooleanField(default=True)),
                ('time', models.DateTimeField()),
                ('text', models.CharField(max_length=4096)),
                ('recip', models.ForeignKey(related_name='message_recip', to='social.Member')),
                ('user', models.ForeignKey(related_name='message_user', to='social.Member')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('text', models.CharField(max_length=4096)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='profile',
            field=models.OneToOneField(null=True, to='social.Profile'),
        ),
    ]
