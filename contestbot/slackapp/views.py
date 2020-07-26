from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import os
import requests
import json
from .resources import *


@method_decorator(csrf_exempt, name='dispatch')
class GetFile(View):
    '''Обработка команды /getfile 
       К каждой команде можно привязать отдельный url для обработки на странице
       https://api.slack.com/apps/A017QMWA0Q3/slash-commands? 
    '''
    def post(self, request):
        '''slack присылает post запрос на указанный url. Все параметры
           которые есть в запросе можно посмотреть в словаре request.POST
        '''
        username = request.POST.get('user_name')
        command = request.POST.get('command')
        text = request.POST.get('text')
        response_url = request.POST.get('response_url')
        channel_name = request.POST.get('channel_name')
        channel_id = request.POST.get('channel_id')
        if text == 'test1':
            #тут я проверяю какой текст передан после комады /getfile 
            slack_send_file(channel_id)
            return HttpResponse('', 200)

        #Отвечаем с кодом 200. Текст ответа прийдет как сообщение от бота.
        return HttpResponse(f'В моей базе пока есть только один файл - test1', 200)


def slack_send_file(channel, **kwargs):
    '''функция отправляет файл в канал отуда получен запрос
       Для примера создал файлик в директории media
    '''

    file_path = os.path.join(settings.MEDIA_ROOT, 'test.doc')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            files = {'file': fh}
            #В словаре date обязательные поля только token и channels
            data = {
                "token": settings.SLACK_BOT_TOKEN,
                "channels": [channel,],
                "filename": "test.doc",
                "initial_comment": "Держи файлик с исходными данными *Теста 1*.\nУ тебя осталось *2* подсказки.\nУдачного обучения!",
                "title": "ТЕСТ 1",
            }
            #Если мы передадим в функцию дополнительные именованные аргументы, они будут включены в словарь
            data.update(kwargs)

            response = requests.post(
                url="https://slack.com/api/files.upload",
                files=files,
                data=data
            )

            '''Можем тут распечатать ответ слака на запрос
               Если есть ошибки, они будут в ответе
               print(f" {response.status_code}: {response.text}" )
            '''


@method_decorator(csrf_exempt, name='dispatch')
class onInteractiv(View):
    '''Обработчик интерактивных событий. К таким событиям относятся нажатия на кнопки,
       отправка форм, еще какие-то взаимодействия с ботом...
       в request.POST получаем payload где есть type. В зависимости от типа действия мы можем
       применять различную логику.
       https://api.slack.com/apps/A017QMWA0Q3/interactive-messages?
    '''

    def post(self, request):
        interactive_action = json.loads(request.POST.get('payload'))
        write_json(interactive_action)
        '''Удобная функция, которая записывает каждый прилетающий запрос
           в удобочитаемом виде в файле answer.json
           Попробуйте, очень удобно читать 
        '''
        if interactive_action["type"] == "interactive_message":
            pass
        
        
        elif interactive_action["type"] == "dialog_submission":
            '''Обработка диалоговой формы'''
            callback_id = interactive_action["callback_id"]
            if callback_id == 'register_form':
                '''Можем что-то сделать с данными
                   Для примера я получаю значение и полей Имя, Почта и Когорта 
                   Просто печатаю их. Хотя нужно сохронять в БД)
                '''
                submission = interactive_action["submission"]
                name = submission['name']
                email = submission['email']
                kogort = submission['kogort']
                print(f'Имя - {name}')
                print(f'Почта - {email}')
                print(f'Когорта - {kogort}')
           
                channel = interactive_action["channel"]['id']
                slack_post_msg(text='Я тебя запомнил!', channel=channel)

        elif interactive_action["type"] == "block_actions":
            '''Обработка нажатия кнопки'''
            user = interactive_action["user"]["id"]
            button = interactive_action["actions"][0]["value"]
            channel = interactive_action["channel"]['id']
            if button == 'click_me_123':
                '''У кнопок задаются уникальные значения для идентификации нажатия на определенной кнопке'''
                slack_post_msg(text='Котику понравилось!', channel=channel)
            elif button == 'click_me_1234':
                #Мы можем добавлять дополнительные вложения к сообщениям - https://api.slack.com/methods/chat.postMessage#arg_attachments
                attachments = json.dumps(photo_barsik)

                #добавляем к сообщению блок с кнопкой Погладить котика - barsik из resourses.py
                blocks = json.dumps(barsik)

                slack_post_msg(text='', channel=channel, attachments=attachments, blocks=blocks)

        '''Внимание!!! Нужно ответить пустым текстом, иначе будет ошибка'''        
        return HttpResponse('', 200)


@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    '''Обработчик команды /register'''

    def post(self, request):


        data = {
            "token": settings.SLACK_BOT_TOKEN,
            'trigger_id': request.POST.get('trigger_id'),
            "dialog": json.dumps(dialog_plot)
            #dialog_plot - это словарь в котором описана форма из файла resource.py
        }

        response = requests.post(
            url="https://slack.com/api/dialog.open",
            data=data
        )
 
        return HttpResponse("Давай познакомимся...", 200)


def slack_post_msg(text, channel, **kwargs):
    '''Эта функция может отправлять сообщения от имени бота в любой канал или в личку'''
    data = {
        "token": settings.SLACK_BOT_TOKEN,
        "channel": channel,
        "text": text
    }

    data.update(kwargs)
    

    response = requests.post(
        url="https://slack.com/api/chat.postMessage",
        data=data
    )

    #print(f"response from 'send_webhook' {response.status_code}: {response.text}" )


def slack_send_webhook(text, channel, **kwargs):
    '''Эта функция отвечает только в тот канал, где зарегистрирован бот
       Не понял смысла в ее использовании
       https://api.slack.com/apps/A017QMWA0Q3/incoming-webhooks?
    '''

    data = {
        "channel": channel,
        "text": text
    }

    data.update(kwargs)

    response = requests.post(
        url=settings.SLACK_WEBHOOK_INC,
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )



@method_decorator(csrf_exempt, name='dispatch')
class Event(View):
    '''Обработчик событий к которым бот имеет доступ
       Настраивается на странице https://api.slack.com/apps/A017QMWA0Q3/event-subscriptions?
       Для примера я отлавливаю событие - получение личного сообщения

       Для подключения данного обработчика нужно ответить на проверочное сообщение с параметром challenge из запроса
       challenge = body['challenge']
       context = {"challenge": challenge,}
       return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    '''

    def post(self, request):
        '''Тут подлянка, данные прилетают в request.body и их нужно декодировать'''
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        write_json(body)
        #print(body)
        subtype = body['event'].get('subtype')
        bot_id = body['event'].get('bot_id')
        text = f"*{body['event']['text']}*"

        if subtype is None and bot_id is None:
            '''Я не знаю пока как правильно проверить от человека прилетело событие или от бота
               Если не делать такую проверку, то бот при ответе фиксирует новое событие и начинает на него отвечать
               Отвечает сам себе бесконечно. Я тут проверяю, если есть подтип (там подтип -бот) и если есть bot_id,
               то не реагируем на такое событие
            '''
            
            #добавляем к сообщению блок с кнопкой Хочу котика - cat из resourses.py
            blocks = json.dumps(cat)
            slack_post_msg(
                text=text, 
                channel=body['event']['channel'],  
                blocks=blocks,
                icon_emoji=':chart_with_upwards_trend:',
                #attachments=attachments
          
                )
        return HttpResponse("ok", 200)


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
