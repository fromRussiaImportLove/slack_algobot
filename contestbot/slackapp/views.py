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
from .resources import dialog_plot

@method_decorator(csrf_exempt, name='dispatch')
class SendFile(View):

    def post(self, request):
        #print(request.POST)
        username = request.POST.get('user_name')
        command = request.POST.get('command')
        text = request.POST.get('text')
        response_url = request.POST.get('response_url')
        channel_name = request.POST.get('channel_name')
        channel_id = request.POST.get('channel_id')
        slack_send_file(channel_id)

        return HttpResponse('Вот держи файлик с ответами! ))')


def slack_send_file(channel, **kwargs):
    file_path = os.path.join(settings.MEDIA_ROOT, 'test.doc')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            files = {'file': fh}
            data = {
                "token": settings.SLACK_BOT_TOKEN,
                "channels": [channel,],
            }

            data.update(kwargs)

            response = requests.post(
                url="https://slack.com/api/files.upload",
                files=files,
                data=data
            )
            #print(f" {response.status_code}: {response.text}" )
 



@method_decorator(csrf_exempt, name='dispatch')
class onInteractiv(View):

    def post(self, request):

        interactive_action = json.loads(request.POST.get('payload'))
        if interactive_action["type"] == "interactive_message":
            pass

        elif interactive_action["type"] == "dialog_submission":
            callback_id = interactive_action["callback_id"]
            if callback_id == 'register_form':
                '''Можем что-то сделать с данными'''
                submission = interactive_action["submission"]
                name = submission['name']
                email = submission['email']
                kogort = submission['kogort']
                print(f'Имя - {name}')
                print(f'Почта - {email}')
                print(f'Когорта - {kogort}')
           
                channel = interactive_action["channel"]['id']
                slack_post_msg(text='Я тебя запомнил!', channel=channel)
                
        return HttpResponse('', 200)


@method_decorator(csrf_exempt, name='dispatch')
class Register(View):

    def post(self, request):

        data = {
            "token": settings.SLACK_BOT_TOKEN,
            'trigger_id': request.POST.get('trigger_id'),
            "dialog": json.dumps(dialog_plot)
        }

        response = requests.post(
            url="https://slack.com/api/dialog.open",
            data=data
        )

        #print(response) 
        return HttpResponse("Давай познакомимся...", 200)


def slack_post_msg(text, channel, **kwargs):
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