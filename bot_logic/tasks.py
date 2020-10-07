from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from algobot.celery import app
from django.conf import settings
from slack import WebClient

from .models import ResponseTasks, Restriction, UserTestPair
from .services import slack_send_file

client = WebClient(token=settings.SLACK_BOT_TOKEN)


@app.task
def send_to_response_url():
    '''
       Каждые 10 секунд проверяем есть ли задачи по отправке тестов
       пользователю. Если задач нет, ничего не делаем, если есть, перебираем
       все, отправляем тесты после чего удаляем задачу. Задачи хранятся в БД в
       моделе ResponseTasks.
    '''
    tasks_list = ResponseTasks.objects.all()
    if tasks_list != []:
        for task in tasks_list:
            student = task.student
            test = task.test
            slack_id = student.slack_id

            restriction, _ = Restriction.objects.get_or_create(
                    user=student, problem=test.problem,
                    contest=test.problem.contest)

            if (UserTestPair.objects.filter(user=student, test=test).exists()
               or restriction.is_in_limit()):
                client.chat_postMessage(
                    channel=f'@{slack_id}',
                    text=f'<@{slack_id}>, вот ваш test#{test.id}, ')
                slack_send_file(
                    slack_id, test.input_file,
                    filename=f'test{test.id}-input.txt',
                    title='Входные данные')
                slack_send_file(
                    slack_id, test.output_file,
                    filename=f'test{test.id}-output.txt', title='Ответ')
                _, new_get_test = UserTestPair.objects.get_or_create(
                    user=student, test=test)

                if new_get_test:
                    restriction.request_counter += 1
                    restriction.save()
            else:
                client.chat_postMessage(
                    channel=f'@{slack_id}',
                    text=f'<@{slack_id}>, ваш лимит подсказок исчерпан')

            task.delete()
