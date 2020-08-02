from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import os
import requests
import json
from .resources import *
import slack
from django.contrib.auth import get_user_model
from .models import Hint, Test, Problem
from .serviсes import *


User = get_user_model()


client = slack.WebClient(token=settings.SLACK_BOT_TOKEN)


@method_decorator(csrf_exempt, name='dispatch')
class GetTest(View):
    '''Обработка команды /gettest'''

    def post(self, request):
        """slack присылает post запрос на указанный url. Все параметры
           которые есть в запросе можно посмотреть в словаре request.POST
        """
        client.dialog_open(trigger_id=request.POST.get(
            'trigger_id'), dialog=json.dumps(choose_test))
        return HttpResponse("Выбирай!", 200)


@method_decorator(csrf_exempt, name='dispatch')
class GetHint(View):
    '''Обработка команды /gethint'''

    def post(self, request):
        client.dialog_open(trigger_id=request.POST.get(
            'trigger_id'), dialog=json.dumps(choose_hint))
        return HttpResponse("Выбирай!", 200)


@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    '''Обработчик команды /register'''

    def post(self, request):
        client.dialog_open(trigger_id=request.POST.get(
            'trigger_id'), dialog=json.dumps(dialog_plot))
        return HttpResponse("Давай познакомимся! :)", 200)


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
        if interactive_action["type"] == "interactive_message":
            pass

        elif interactive_action["type"] == "dialog_submission":
            '''Обработка диалоговой формы'''
            submission = interactive_action["submission"]
            channel = interactive_action["channel"]['id']
            callback_id = interactive_action["callback_id"]
            if callback_id == 'register_form':
                name = submission['name']
                email = submission['email']
                kogort = submission['kogort']
                # Пока так, потом надо переделать на id пользователя
                if User.objects.filter(username=name):
                    client.chat_postMessage(
                        channel=channel, text='Маска, я тебя знаю!')
                else:
                    new_user = User.objects.create(username=name, email=email)
                    new_user.save()
                    client.chat_postMessage(
                        channel=channel, text='Приятно познакомиться!')
            if callback_id == 'test_form':
                task = submission['task']
                test = submission['test']
                if Test.objects.filter(problem__title=task, number=test).exists():
                    result = Test.objects.get(problem__title=task, number=test)
                    title = 'Done!'
                    client.files_upload(
                        channels=channel, title=title, file=result.test_file.path)
                else:
                    client.chat_postMessage(
                        channel=channel, text='У меня такого нет :(')
            if callback_id == 'prompt_form':
                task = submission['task']
                if Hint.objects.filter(problem__title=task).exists():
                    prompt = Hint.objects.get(problem__title=task)
                    client.chat_postMessage(channel=channel, text=prompt.text)
                else:
                    client.chat_postMessage(
                        channel=channel, text='У меня такого нет :(')

        elif interactive_action["type"] == "block_actions":
            '''Обработка нажатия кнопки'''
            user = interactive_action["user"]["id"]
            button = interactive_action["actions"][0].get("value")
            block_id = interactive_action["actions"][0].get("block_id")
            action_id = interactive_action["actions"][0].get("action_id")
            selected_option = interactive_action[
                "actions"][0].get("selected_option")
            channel = interactive_action["channel"]['id']

            if button == 'click_me_123':
                '''У кнопок задаются уникальные значения для идентификации нажатия на определенной кнопке'''
                client.chat_postMessage(
                    text='Котику понравилось!', channel=channel)

            elif button == 'click_me_1234':
                client.chat_postMessage(
                    channel=channel, text='', blocks=build_test_block())

            elif button == 'click_me_test':
                print(interactive_action['trigger_id'])
                client.dialog_open(trigger_id=interactive_action[
                                   'trigger_id'], dialog=json.dumps(choose_test))

            elif button == 'click_me_hint':
                client.dialog_open(trigger_id=interactive_action[
                                   'trigger_id'], dialog=json.dumps(choose_hint))

            elif block_id == 'choose_test':
                '''Обработка выбора селекта с тестами'''
                test, ts = choose_test(request)
                # Обновляем сообщение
                client.chat_update(
                    channel=channel, ts=ts, blocks=test_section(test))

        '''Внимание!!! Нужно ответить пустым текстом, иначе будет ошибка'''
        return HttpResponse('', 200)


@method_decorator(csrf_exempt, name='dispatch')
class Event(View):
    '''Обработчик событий к которым бот имеет доступ
       Для подключения данного обработчика нужно ответить на проверочное сообщение с параметром challenge из запроса
       challenge = body['challenge']
       context = {"challenge": challenge,}
       return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")
    '''

    def post(self, request):

        body = json.loads(request.body.decode('utf-8'))
        if body.get('token') != settings.SLACK_VERIFY_TOKEN:
            return HttpResponse(status=403)
        if 'type' in body:
            if body.get('type') == 'url_verification':
                response = {'challenge': body['challenge']}
                return JsonResponse(response, safe=False)
        if 'event' in body:
            event = body['event']
            if event.get('subtype') == 'bot_message':
                return HttpResponse(status=200)
            user = event.get('user')
            channel = event.get('channel')
            text = event.get('text')
            event_type = event.get('type')
            if event_type == 'app_home_opened':
                # Если пользователь открыл чат с ботом
                # добавляем к сообщению блок с кнопкой Хочу котика - cat из
                # resourses.py
                blocks = json.dumps(cat)
                client.chat_postMessage(
                    channel=channel, text=text, blocks=blocks, icon_emoji=':chart_with_upwards_trend:')

            elif event_type == 'reaction_added':
                # Пользователь добавил реакцию(смайл) к сообщению
                channel = event['item'].get('channel')
                if event['reaction'] == '+1':
                    text = f'Отлично, <@{user}>!, спасибо что прочитал! :yum:'
                else:
                    text = f'Не та реакция! Я ведь просил :+1: !'

                client.chat_postMessage(channel=channel, text=text)

            elif event_type == 'reaction_removed':
                # удалил реакцию
                text = f'Что? <@{user}>,ты передумад? :zany_face:'
                channel = event['item'].get('channel')
                client.chat_postMessage(channel=channel, text=text)

            elif event_type == 'app_mention':
                blocks = json.dumps(choose_your_destiny)
                text = f'Привет! Чем могу помочь? Выбирай с умом'
                client.chat_postMessage(
                    channel=channel, text=text, blocks=blocks)
            else:
                if text == 'Привет':
                    client.chat_postMessage(channel=channel, text=f'Привет, <@{user}>! :tada:')

        return HttpResponse("ok", 200)


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
