from django.conf import settings
from .models import Hint, Test, Problem
import os
import json
import requests


def slack_send_file(channel, text, value, **kwargs):
    '''функция отправляет файл в канал отуда получен запрос'''

    files = create_path_to_file(value)
    if files is not None:
        # В словаре date обязательные поля только token и channels
        data = {
            "token": settings.SLACK_BOT_TOKEN,
            "channels": [channel, ],
            "filename": "test.txt",
            #"initial_comment": "Держи файлик с исходными данными *Теста 1*.\nУ тебя осталось *2* подсказки.\nУдачного обучения!",
            "title": f"ТЕСТ {text}",
        }
        # Если мы передадим в функцию дополнительные именованные аргументы, они
        # будут включены в словарь
        data.update(kwargs)

        response = requests.post(
            url="https://slack.com/api/files.upload",
            files=files,
            data=data
        )


def create_path_to_file(id):
    test = Test.objects.get(id=id)
    test_file = test.test_file

    return {'file': test_file}


def choose_test(request):
    interactive_action = json.loads(request.POST.get('payload'))
    selected_option = interactive_action[
        "actions"][0].get("selected_option")
    channel = interactive_action["channel"]['id']
    value = selected_option.get("value")
    text = selected_option["text"].get("text")
    ts = interactive_action["message"]["ts"]
    # Отправляем файл с тестом
    slack_send_file(channel, text, value)
    test = Test.objects.get(id=value)

    return test, ts


def build_test_block():
    tests = Test.objects.all()

    options = []
    for test in tests:
        data = {
            "text": {
                "type": "plain_text",
                "text": f"Спринт:{test.problem.sprint_number} | Контест:{test.problem.contest_number} | Задача:{test.problem.title} | Тест:{test.number}"
            },
            "value": str(test.id)
        }
        options.append(data)

    block = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "На какой тест нужны исходные данные?"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "block_id": "choose_test",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Выбери тест"
                    },
                    "action_id": "action2",
                    "options": options

                },
            ]
        }]

    return block
