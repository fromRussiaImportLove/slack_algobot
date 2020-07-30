from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import os


User = get_user_model()


class Problem(models.Model):
    sprint_number = models.CharField(
        max_length=255, verbose_name='Номер спринта')
    contest_number = models.CharField(
        max_length=255, verbose_name='Номер контеста')
    title = models.CharField(max_length=3, verbose_name='Название задачи')

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return f'Спринт: {self.sprint_number}, Контест: {self.contest_number}, Задача: {self.title}'


class Test(models.Model):

    def file_name(instance, filename):
        '''Генерируем путь и имя сохроняемого файла
           Получаем расширение, контест, задачу. Формируем путь, имя файла.
           Если файл уже существует, удаляем его перед сохранением.
        '''
        ext = filename.split('.')[-1]
        contest = str(instance.problem.contest_number)
        task = str(instance.problem.title)
        path = contest + '/' + task + '/'
        filename = "%s.%s" % (instance.number, ext)
        fullname = os.path.join(settings.MEDIA_ROOT,
                                'tests_files/', path, filename)
        if os.path.exists(fullname):
            os.remove(fullname)

        return 'tests_files/' + path + filename

    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name='test', verbose_name='Задача')
    number = models.CharField(max_length=3, verbose_name='Номер теста')
    test_file = models.FileField(
        upload_to=file_name)

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        return self.number


class Hint(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name='hint', verbose_name='Задача')
    text = models.TextField(verbose_name='Текст подсказки')

    class Meta:
        verbose_name = "Подсказка"
        verbose_name_plural = "Подсказки"

    def __str__(self):
        return self.text


class Restriction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='test_counter', verbose_name='Студент')
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name='test_counter', verbose_name='Задача')
    counter = models.SmallIntegerField(
        default=3, verbose_name='Количество оставшихся тестов')

    class Meta:
        verbose_name = "Ограничение"
        verbose_name_plural = "Ограничения"

    def __str__(self):
        return f'{self.user}, Задача: {self.problem}'
