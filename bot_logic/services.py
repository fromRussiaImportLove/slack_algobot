import os
import json

import requests
from django.conf import settings


def options_generator(objects_list, slack_id=None):
    '''Генератор списка опций. На вход принимает QuerySet из объектов.
    Возвращает массив из набора опций'''
    options = []
    for item in objects_list:
        text = str(item)
        # Получаем текст из метода get_hint если есть аргумент slack_id
        if slack_id is not None:
            text = str(item.get_hint(slack_id))
        option = {
            "text": {
                "type": "plain_text",
                "text": text
            },
            "value": str(item.pk)
        }
        options.append(option)
    return options


def validation_generator(errors):
    '''Составляет словарь ошибок валидации для json ответа в слак'''
    for key in errors:
        errors[key] = ' '.join(errors[key])
    response = {
        "response_action": "errors",
        "errors": errors
    }
    return response


def slack_send_file(channel, path, **kwargs):
    '''функция отправляет файл в канал отуда получен запрос
       Для примера создал файлик в директории media
    '''

    file_path = os.path.join(settings.MEDIA_ROOT, str(path))
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            files = {'file': fh}
            # В словаре date обязательные поля только token и channels
            data = {
                "token": settings.SLACK_BOT_TOKEN,
                "channels": [channel, ],
                # "filename": "test.doc",
                # "initial_comment":"Держи файлик с исходными данными *Теста 1*
                # \nУ тебя осталось *2* подсказки.\nУдачного обучения!",
                # "title": "ТЕСТ 1",
            }
            # Если мы передадим в функцию дополнительные именованные аргументы,
            # они будут включены в словарь
            data.update(kwargs)

            requests.post(url="https://slack.com/api/files.upload",
                          files=files,
                          data=data)

            '''Можем тут распечатать ответ слака на запрос
               Если есть ошибки, они будут в ответе
               print(f" {response.status_code}: {response.text}" )
            '''


def send_to_response_url(url):
    data = {"text": 'Тестим фичу', }
    response = requests.post(url=url, data=json.dumps(data))
    print(f" {response.status_code}: {response.text}")
