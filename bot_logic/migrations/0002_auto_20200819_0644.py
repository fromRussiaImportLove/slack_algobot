# Generated by Django 3.0.8 on 2020-08-19 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_logic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hint',
            name='number',
            field=models.IntegerField(verbose_name='Номер подсказки'),
        ),
        migrations.AlterUniqueTogether(
            name='hint',
            unique_together={('number', 'problem')},
        ),
    ]
