# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-01 18:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('start', '0002_remove_person_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=180, null=True)),
                ('person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='start.Person')),
            ],
        ),
        migrations.RemoveField(
            model_name='location',
            name='person',
        ),
        migrations.RemoveField(
            model_name='adoptionproposal',
            name='p1',
        ),
        migrations.RemoveField(
            model_name='adoptionproposal',
            name='p2',
        ),
        migrations.AddField(
            model_name='adoptionproposal',
            name='adopter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adopter', to='start.Person'),
        ),
        migrations.AddField(
            model_name='adoptionproposal',
            name='person_give',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='person_give', to='start.Person'),
        ),
        migrations.AlterField(
            model_name='animalreport',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='start.Place'),
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
