from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Sprint(models.Model):
    title = models.CharField(max_length=255)
    number = models.CharField(max_length=3)

    def __str__(self):
        return self.number


class Contest(models.Model):
    sprint_number = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, related_name='contest', null=True, default='NULL')
    title = models.CharField(max_length=255)
    number = models.CharField(max_length=255)

    def __str__(self):
        return self.number


class Problem(models.Model):
    sprint_number = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, related_name='problem', null=True, default='NULL')
    contest_number = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name='problem')
    title = models.CharField(max_length=3)

    def __str__(self):
        return self.title


class Test(models.Model):
    problem_title = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name='test')
    number = models.CharField(max_length=3)
    test_file = models.FileField(
        upload_to='tests_files/')

    def __str__(self):
        return self.number


class Hint(models.Model):
    problem_title = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name='hint')
    text = models.TextField()

    def __str__(self):
        return self.text


class TestRestriction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='test_counter')
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name='test_counter')
    counter = models.SmallIntegerField(default=3)

    def __str__(self):
        return self.counter
