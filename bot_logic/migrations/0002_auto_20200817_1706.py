# Generated by Django 3.0.8 on 2020-08-17 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot_logic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userhintpair',
            name='hint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_hint_pair', to='bot_logic.Hint', verbose_name='Подсказка'),
        ),
    ]
