from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json
from .resources import anonymous_greeting, user_greeting, register_form
from slack import WebClient
from .models import User


client = WebClient(token=settings.SLACK_BOT_TOKEN)


@method_decorator(csrf_exempt, name='dispatch')
class onInteractive(View):
    '''Обработчик нажатий на кнопки'''
    def post(self, request):
        payload = json.loads(request.POST.get('payload'))
        payload_type = payload['type']
        if payload_type == 'block_actions':
            button = payload["actions"][0].get('value')
            if button == 'click_me_register':
                user_registration(payload)
        if payload_type == 'view_submission':
            callback_id = payload['view']['callback_id']
            if callback_id == 'register-form':
                user_registration(payload)
        return HttpResponse('', 200)


@method_decorator(csrf_exempt, name='dispatch')
class Event(View):
    '''Обработчик событий. Выводит сообщение когда пользователь
    открывает диалог с ботом'''
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
            event_type = event.get('type')

            if User.objects.filter(slack_id=user).exists():
                greeting = user_greeting(user)
            else:
                greeting = anonymous_greeting

            if event_type == 'app_home_opened':
                client.chat_postMessage(
                    channel=channel, blocks=greeting)

            if event_type == 'app_mention':
                client.chat_postMessage(
                    channel=channel, blocks=greeting)

        return HttpResponse("ok", 200)


def user_registration(payload):
    '''Вывод формы регистрации и добавление пользователя в базу'''
    slack_id = payload['user']['id']
    if User.objects.filter(slack_id=slack_id).exists():
        channel = payload['channel']['id']
        text = f'Мы уже знакомы, <@{slack_id}>!'
        client.chat_postMessage(channel=channel, text=text)
        return

    if payload['type'] == 'block_actions':
        client.views_open(trigger_id=payload['trigger_id'],
                          view=json.dumps(register_form))
        return

    first_name = payload['view']['state']['values']['first-name']['0']['value']
    last_name = payload['view']['state']['values']['last-name']['0']['value']
    email = payload['view']['state']['values']['email']['0']['value']
    cohort = payload['view']['state']['values']['cohort']['0']['value']
    User.objects.create(first_name=first_name, last_name=last_name,
                        email=email, cohort=int(cohort), slack_id=slack_id)

    client.chat_postMessage(channel=f'@{slack_id}',
                            blocks=user_greeting(slack_id))
