from django.db import models
from django.db.models import Sum
from django.conf import settings
from pytz import timezone


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


class Student(models.Model):
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Электронная почта')
    slack_id = models.CharField(
        max_length=255, unique=True, verbose_name='id в Слаке')
    cohort = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name='Когорта')
    specialty = models.ForeignKey(
        Specialty, on_delete=models.SET_NULL, related_name='user',
        blank=True, null=True, verbose_name='Специальность')

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return f'{self.first_name} {self.last_name}, когорта {self.cohort}'


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
        return f'{self.title}. {self.full_title}'

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
    number = models.IntegerField(verbose_name='Номер подсказки')

    class Meta:
        unique_together = ('number', 'problem')
        ordering = ["number"]
        verbose_name = 'Подсказка'
        verbose_name_plural = 'Подсказки'

    def __str__(self):
        return str(self.number)

    def get_text(self):
        return self.text

    def get_hint(self, slack_id):
        student = Student.objects.get(slack_id=slack_id)
        if UserHintPair.objects.filter(hint=self, user=student).exists():
            tz = settings.TIME_ZONE
            timestamp = UserHintPair.objects.get(
                hint=self, user=student).timestamp.astimezone(timezone(tz))
            timestamp = timestamp.strftime('%d.%m.%Y %H:%M')    
            return f'{self.number} - Вы уже брали эту подсказку {timestamp}'

        return self.number


class Restriction(models.Model):
    user = models.ForeignKey(
        Student, on_delete=models.CASCADE,
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
        Student, on_delete=models.CASCADE,
        related_name='user_test_pair', verbose_name='Студент')
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE,
        related_name='user_test_pair', verbose_name='Тест')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запрошенный студентом тест'
        verbose_name_plural = 'Запрошенные студентами тесты'


class UserHintPair(models.Model):
    user = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='user_hint_pair', verbose_name='Студент')
    hint = models.ForeignKey(
        Hint, on_delete=models.CASCADE,
        related_name='user_hint_pair', verbose_name='Подсказка')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Запрошенная студентом подсказка'
        verbose_name_plural = 'Запрошенные студентами подсказки'


class ResponseTasks(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='response_task_student', verbose_name='Студент')
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE,
        related_name='response_task_test', verbose_name='Тест')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи(response_url)'
