from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    slack_id = models.PositiveSmallIntegerField(
        unique=True, verbose_name='id в Слаке', blank=True, null=True)
    cohort = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name='Когорта')

    def __str__(self):
        return f'{self.get_full_name()}, когорта {self.cohort}'


class Sprint(models.Model):
    faculty = models.CharField(
        max_length=255, verbose_name='Факультет',
        blank=True, null=True)
    sprint_number = models.PositiveSmallIntegerField(
        verbose_name='Номер спринта')
    sprint_title = models.CharField(
        max_length=255, verbose_name='Название спринта')

    class Meta:
        verbose_name = 'Спринт'
        verbose_name_plural = 'Спринты'

    def __str__(self):
        return f'{str(self.sprint_number)}. {self.sprint_title}'


class Contest(models.Model):
    contest_number = models.PositiveSmallIntegerField(
        verbose_name='Номер контеста')  # unqiue=True?
    contest_title = models.CharField(
        max_length=255, verbose_name='Название контеста')
    sprint_number = models.ForeignKey(  # возможно manytomany
        Sprint, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='contest', verbose_name='Спринт')

    class Meta:
        verbose_name = "Контест"
        verbose_name_plural = "Контесты"

    def __str__(self):
        return f'{str(self.contest_number)}. {self.contest_title}'


class Problem(models.Model):
    sprint_number = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='problem', verbose_name='Спринт')
    contest_number = models.ForeignKey(
        Contest, on_delete=models.CASCADE,
        related_name='problem', verbose_name='Контест')
    title = models.CharField(max_length=3, verbose_name='Название задачи')
    full_title = models.CharField(
        max_length=255, verbose_name='Полное название')
    test_limit = models.PositiveSmallIntegerField(
        default=3, verbose_name='Лимит тестов')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return (f'{self.sprint_number} '
                f'{self.contest_number} '
                f'{self.title}. '
                f'{self.full_title}')


class Test(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE,
        related_name='test', verbose_name='Задача')
    number = models.PositiveSmallIntegerField(verbose_name='Номер теста')
    test_file = models.FileField(
        upload_to='tests_files/')

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return f'{self.problem}. Тест №{str(self.number)}'


class Hint(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE,
        related_name='hint', verbose_name='Задача')
    text = models.TextField(verbose_name='Текст подсказки')

    class Meta:
        verbose_name = 'Подсказка'
        verbose_name_plural = 'Подсказки'

    def __str__(self):
        return self.text


class Restriction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='restriction', verbose_name='Студент')
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE,
        related_name='restriction', verbose_name='Задача')
    request_counter = models.PositiveSmallIntegerField(
        default=0, verbose_name='Количество запросов на тесты')

    def check_request_limit(self, problem):
        return problem.test_limit >= self.request_counter

    def __str__(self):
        return f'{self.user}, Задача: {self.problem}'

    class Meta:
        verbose_name = 'Ограничение'
        verbose_name_plural = 'Ограничения'


class UserTestPair(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='user_test_pair', verbose_name='Студент')
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE,
        related_name='user_test_pair', verbose_name='Тест')

    class Meta:
        verbose_name = 'Запрошенный студентом тест'
        verbose_name_plural = 'Запрошенные студентами тесты'
