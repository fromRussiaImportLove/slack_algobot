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
            "title": f"{text}",
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


def get_atributes(request):
    interactive_action = json.loads(request.POST.get('payload'))
    selected_option = interactive_action[
        "actions"][0].get("selected_option")
    channel = interactive_action["channel"]['id']
    value = selected_option.get("value")
    text = selected_option["text"].get("text")
    ts = interactive_action["message"]["ts"]
    action_id = interactive_action["actions"][0].get("action_id")

    data = {
        'channel': channel,
        'value': value,
        'text': text,
        'ts': ts,
        'action_id': action_id,
    }

    return data


def create_options_data(obj, obj_type):
    if obj_type == 'sprint':
        text = 'Спринт'
    elif obj_type == 'contest':
        text = 'Контест'
    elif obj_type == 'task':
        text = 'Задача'
    elif obj_type == 'test':
        text = 'Тест'
        obj = obj[1]

    data = {
        "text": {
            "type": "plain_text",
            "text": f"{text}: {obj}"
        },
        "value": str(obj)
    }
    return data


def create_options(obj_list, obj_type):
    return [create_options_data(obj, obj_type) for obj in set(obj_list)]


def create_block(options, block_id, action_id, text):
    block = [
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "block_id": block_id,
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": text,
                    },
                    "action_id": action_id,
                    "options": options

                },
            ]
        }]

    return block


def build_sprint_block():
    sprint_number_list = Problem.objects.all().values_list('sprint_number', flat=True)

    options = create_options(sprint_number_list, obj_type='sprint')

    return create_block(options, block_id='choose_sprint', action_id='action_sprint', text='Укажите спринт')


def choose_contest(request):
    data = get_atributes(request)
    contest_list = Problem.objects.filter(
        sprint_number=data['value']).values_list('contest_number', flat=True)
    options = create_options(contest_list, obj_type='contest')

    return create_block(options, block_id='choose_contest', action_id=data['value'], text='Укажите контест')


def choose_task(request):
    data = get_atributes(request)
    sprint_number = data['action_id']
    task_list = Problem.objects.filter(sprint_number=sprint_number,
                                       contest_number=data['value']).values_list('title', flat=True)
    options = create_options(task_list, obj_type='task')
    action_id = f"{sprint_number}__{data['value']}"
    return create_block(options, block_id='choose_task', action_id=action_id, text='Укажите задачу')


def choose_test(request):
    data = get_atributes(request)
    action_id = data['action_id'].split('__')
    sprint_number = action_id[0]
    contest_number = action_id[1]
    test_list = Test.objects.filter(problem__sprint_number=sprint_number,
                                    problem__contest_number=contest_number,).values_list('number', 'id')
    options = create_options(test_list, obj_type='test')
    action_id = f"{sprint_number}__{contest_number}__{data['value']}"

    return create_block(options, block_id='choose_test_final', action_id=action_id, text='Укажите тест')


def choose_test_final(request):
    data = get_atributes(request)
    # Отправляем файл с тестом
    slack_send_file(data['channel'], data['text'], data['value'])
    test = Test.objects.get(id=data['value'])

    return test, data['ts']
