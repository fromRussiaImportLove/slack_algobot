from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum


class Faculty(models.Model):
    title = models.CharField(
        max_length=255, verbose_name='Название факультета')

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'

    def __str__(self):
        return self.title


class Specialty(models.Model):
    title = models.CharField(
        max_length=255, verbose_name='Название специальности')
    faculty = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, related_name='specialty',
        blank=True, null=True, verbose_name='Факультет')

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'

    def __str__(self):
        return self.title


class User(AbstractUser):
    slack_id = models.CharField(
        max_length=255, unique=True, verbose_name='id в Слаке',
        blank=True, null=True)
    cohort = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name='Когорта')
    specialty = models.ForeignKey(
        Specialty, on_delete=models.SET_NULL, related_name='user',
        blank=True, null=True, verbose_name='Специальность')

    def __str__(self):
        return f'{self.get_full_name()}, когорта {self.cohort}'


class Sprint(models.Model):
    specialty = models.ForeignKey(
        Specialty, on_delete=models.SET_NULL, related_name='sprint',
        verbose_name='Специальность', blank=True, null=True)
    number = models.PositiveSmallIntegerField(
        verbose_name='Номер спринта')
    title = models.CharField(
        max_length=255, verbose_name='Название спринта')

    class Meta:
        verbose_name = 'Спринт'
        verbose_name_plural = 'Спринты'

    def __str__(self):
        return f'{self.number}. {self.title}'


class Contest(models.Model):
    number = models.PositiveSmallIntegerField(
        verbose_name='Номер контеста')  # unqiue=True?
    title = models.CharField(
        max_length=255, verbose_name='Название контеста')
    sprint = models.ManyToManyField(
        Sprint, blank=True, related_name='contest',
        verbose_name='Спринт')
    test_limit = models.PositiveSmallIntegerField(
        default=10, verbose_name='Лимит тестов')

    class Meta:
        verbose_name = "Контест"
        verbose_name_plural = "Контесты"

    def __str__(self):
        return f'{self.number}. {self.title}'


class Problem(models.Model):
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE,
        related_name='problem', verbose_name='Контест')
    title = models.CharField(max_length=3, verbose_name='Номер задачи')
    full_title = models.CharField(
        max_length=255, verbose_name='Полное название')
    test_limit = models.PositiveSmallIntegerField(
        default=3, verbose_name='Лимит тестов')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return (f'{self.sprint}'
                f'{self.contest} '
                f'{self.title}. '
                f'{self.full_title}')

    @property
    def sprint(self):
        return self.contest.sprint.first()


class Test(models.Model):
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE,
        related_name='test', verbose_name='Задача')
    number = models.PositiveSmallIntegerField(verbose_name='Номер теста')
    input_file = models.FileField(
        upload_to='tests_files/',
        verbose_name='Входные данные')
    output_file = models.FileField(
        upload_to='tests_files/', verbose_name='Ответ')

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
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE,
        related_name='restriction', verbose_name='Контест')
    request_counter = models.PositiveSmallIntegerField(
        default=0, verbose_name='Количество запросов на тесты')

    class Meta:
        verbose_name = 'Ограничение'
        verbose_name_plural = 'Ограничения'

    def __str__(self):
        return f'{self.user}, Задача: {self.problem}'

    def is_in_limit(self):
        contest_counter = Restriction.objects.filter(
            user=self.user, contest=self.contest).aggregate(
                result=Sum('request_counter'))
        return (self.problem.test_limit > self.request_counter and
                self.contest.test_limit > contest_counter['result'])


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
