
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(
                    verbose_name='Номер контеста')),
                ('title', models.CharField(max_length=255,
                                           verbose_name='Название контеста')),
                ('test_limit', models.PositiveSmallIntegerField(
                    default=10, verbose_name='Лимит тестов')),
            ],
            options={
                'verbose_name': 'Контест',
                'verbose_name_plural': 'Контесты',
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255,
                                           verbose_name='Название факультета')),
            ],
            options={
                'verbose_name': 'Факультет',
                'verbose_name_plural': 'Факультеты',
            },
        ),
        migrations.CreateModel(

            name='Hint',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст подсказки')),
                ('number', models.IntegerField(verbose_name='Номер подсказки')),

            ],
            options={
                'verbose_name': 'Подсказка',
                'verbose_name_plural': 'Подсказки',

                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(


            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=3, verbose_name='Номер задачи')),
                ('full_title', models.CharField(
                    max_length=255, verbose_name='Полное название')),
                ('test_limit', models.PositiveSmallIntegerField(
                    default=3, verbose_name='Лимит тестов')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='problem', to='bot_logic.Contest', verbose_name='Контест')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
            },
        ),
        migrations.CreateModel(
            name='Specialty',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255,
                                           verbose_name='Название специальности')),
                ('faculty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='specialty', to='bot_logic.Faculty', verbose_name='Факультет')),
            ],
            options={
                'verbose_name': 'Специальность',
                'verbose_name_plural': 'Специальности',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, verbose_name='Имя')),
                ('last_name', models.CharField(
                    max_length=255, verbose_name='Фамилия')),
                ('email', models.EmailField(
                    max_length=254, verbose_name='Электронная почта')),
                ('slack_id', models.CharField(max_length=255,
                                              unique=True, verbose_name='id в Слаке')),
                ('cohort', models.PositiveSmallIntegerField(
                    blank=True, null=True, verbose_name='Когорта')),
                ('specialty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                related_name='user', to='bot_logic.Specialty', verbose_name='Специальность')),
            ],
            options={
                'verbose_name': 'Студент',
                'verbose_name_plural': 'Студенты',
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(
                    verbose_name='Номер теста')),
                ('input_file', models.FileField(
                    upload_to='tests_files/', verbose_name='Входные данные')),
                ('output_file', models.FileField(
                    upload_to='tests_files/', verbose_name='Ответ')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='test', to='bot_logic.Problem', verbose_name='Задача')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
            },
        ),
        migrations.CreateModel(
            name='UserTestPair',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),

                ('timestamp', models.DateTimeField(auto_now_add=True)),

                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='user_test_pair', to='bot_logic.Test', verbose_name='Тест')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='user_test_pair', to='bot_logic.Student', verbose_name='Студент')),
            ],
            options={
                'verbose_name': 'Запрошенный студентом тест',
                'verbose_name_plural': 'Запрошенные студентами тесты',
            },
        ),
        migrations.CreateModel(
            name='UserHintPair',
            fields=[

                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),

                ('timestamp', models.DateTimeField(
                    auto_now_add=True, verbose_name='Дата')),
                ('hint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='user_hint_pair', to='bot_logic.Hint', verbose_name='Подсказка')),

                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='user_hint_pair', to='bot_logic.Student', verbose_name='Студент')),

            ],
            options={
                'verbose_name': 'Запрошенная студентом подсказка',
                'verbose_name_plural': 'Запрошенные студентами подсказки',
            },
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(
                    verbose_name='Номер спринта')),
                ('title', models.CharField(
                    max_length=255, verbose_name='Название спринта')),
                ('specialty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                related_name='sprint', to='bot_logic.Specialty', verbose_name='Специальность')),
            ],
            options={
                'verbose_name': 'Спринт',
                'verbose_name_plural': 'Спринты',
            },
        ),
        migrations.CreateModel(
            name='Restriction',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('request_counter', models.PositiveSmallIntegerField(
                    default=0, verbose_name='Количество запросов на тесты')),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='restriction', to='bot_logic.Contest', verbose_name='Контест')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='restriction', to='bot_logic.Problem', verbose_name='Задача')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='restriction', to='bot_logic.Student', verbose_name='Студент')),
            ],
            options={
                'verbose_name': 'Ограничение',
                'verbose_name_plural': 'Ограничения',
            },
        ),

        migrations.CreateModel(
            name='ResponseTasks',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(
                    auto_now_add=True, verbose_name='Дата создания')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='response_task_student', to='bot_logic.Student', verbose_name='Студент')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='response_task_test', to='bot_logic.Test', verbose_name='Тест')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи(response_url)',
            },
        ),
        migrations.AddField(
            model_name='hint',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='hint', to='bot_logic.Problem', verbose_name='Задача'),
        ),
        migrations.AddField(

            name='Hint',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст подсказки')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='hint', to='bot_logic.Problem', verbose_name='Задача')),
            ],
            options={
                'verbose_name': 'Подсказка',
                'verbose_name_plural': 'Подсказки',
            },

        ),
        migrations.AddField(

            model_name='contest',
            name='sprint',
            field=models.ManyToManyField(
                blank=True, related_name='contest', to='bot_logic.Sprint', verbose_name='Спринт'),
        ),

        migrations.AlterUniqueTogether(
            name='hint',
            unique_together={('number', 'problem')},
        ),

    ]
