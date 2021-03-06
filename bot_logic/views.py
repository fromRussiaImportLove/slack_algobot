import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from slack import WebClient
from .tasks import send_to_response_url
from .block_hint import GetHintForm
from .models import (Contest, Hint, Problem, ResponseTasks, Specialty, Sprint,
                     Student, Test, UserHintPair)
from .resources import anonymous_greeting, register_form, user_greeting
from .services import options_generator, validation_generator

client = WebClient(token=settings.SLACK_BOT_TOKEN)
hint_form = GetHintForm()


def set_user_hints(slack_id, hint):
    '''Проверяем брал ли данную подсказку конкретный пользователь.
       Если не брал, фиксируем. Если брал - обновляем время
    '''
    student = Student.objects.get(slack_id=slack_id)
    user_hint, created = UserHintPair.objects.get_or_create(
        user=student, hint=hint)
    if not created:
        user_hint.timestamp = timezone.now()
        user_hint.save(update_fields=["timestamp"])


def get_student(slack_id: str) -> Student:
    # Проверяем, является ли пользователь зарегистрированным
    try:
        student = Student.objects.get(slack_id=slack_id)
    except ObjectDoesNotExist:
        return None
    else:
        return student


def get_hint(payload):
    """Вывод формы с запросом спринта/контеста/задачи"""
    slack_id = payload['user']['id']

    student = get_student(slack_id)
    if not student:
        client.chat_postMessage(channel=slack_id, blocks=anonymous_greeting)
        return HttpResponse('', 200)

    if payload['type'] == 'block_actions':
        if payload.get('view'):
            if payload['view'].get('callback_id') == 'get-hint-form':
                client.views_update(view=hint_form(payload),
                                    view_id=payload['view']['id'])
        else:
            client.views_open(trigger_id=payload['trigger_id'],
                              view=hint_form(payload))

    if (payload['type'] == 'view_submission' and
            'block-hint' in payload['view']['state']['values'].keys()):

        block = payload['view']['state']['values']['block-hint']
        hint_id = block['get-form-tips-complete']['selected_option']['value']
        hint = Hint.objects.get(id=hint_id)
        # Создаем или обновляем данные о подсказках
        set_user_hints(slack_id, hint)
        client.chat_postMessage(channel=f'@{slack_id}',
                                text=f'{hint.get_text()}')

    if (payload['type'] == 'view_submission' and
            'block-test' in payload['view']['state']['values'].keys()):

        block = payload['view']['state']['values']['block-test']
        test_id = block['get-form-tips-complete']['selected_option']['value']
        test = Test.objects.get(id=test_id)
        # Создаем задачу для фоновой обработки
        ResponseTasks.objects.create(student=student, test=test)
        #Запускаяем здачу в фоне
        send_to_response_url.delay()

    return HttpResponse('', 200)


@method_decorator(csrf_exempt, name='dispatch')
class OnInteractive(View):
    """Обработчик нажатий на кнопки"""

    def post(self, request):
        payload = json.loads(request.POST.get('payload'))
        payload_type = payload['type']

        if payload_type == 'block_actions':
            button = payload["actions"][0].get('value')
            if button == 'click_me_register':
                response = user_registration(payload)

            if button in ['click_me_hint', 'click_me_test']:
                get_hint(payload)
            if payload.get('view'):
                if payload['view'].get('callback_id') == 'get-hint-form':
                    get_hint(payload)

        if payload_type == 'view_submission':
            callback_id = payload['view']['callback_id']
            if callback_id == 'get-hint-form':
                response = get_hint(payload)
            if callback_id == 'register-form':
                response = user_registration(payload)

        else:
            return HttpResponse('', 200)

        return response


@method_decorator(csrf_exempt, name='dispatch')
class Event(View):
    """Обработчик событий. Выводит сообщение когда пользователь
    открывает диалог с ботом"""

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

            if Student.objects.filter(slack_id=user).exists():
                greeting = user_greeting(user)
            else:
                greeting = anonymous_greeting

            if event_type == 'app_home_opened':
                client.chat_postMessage(
                    channel=channel, blocks=greeting)

            if event_type == 'app_mention':
                client.chat_postMessage(
                    channel=channel, blocks=greeting)

        return HttpResponse('ok', 200)


@method_decorator(csrf_exempt, name='dispatch')
class Select(View):
    """Обработчик запросов external_select. Должен вернуть json ответ
    со списком опций которые можно выбрать в форме"""

    def post(self, request):
        selector = json.loads(request.POST.get('payload'))
        options = []
        blocks = dict()
        if selector.get('block_id') == 'specialty':
            objects_list = Specialty.objects.all()
            options = options_generator(objects_list)

        for num_block, block in enumerate(selector['view']['blocks']):
            if block['block_id'].startswith('block-'):
                current_block = selector['view']['blocks'][num_block]
                if current_block.get('accessory'):
                    accessory = current_block['accessory']
                    if accessory.get('initial_option'):
                        initial_option = accessory['initial_option']
                        blocks[block['block_id'][6:]] = initial_option['value']

        if selector.get('block_id') == 'block-sprint':
            user = Student.objects.get(slack_id=selector['user']['id'])
            specialty = user.specialty
            objects_list = Sprint.objects.filter(specialty=specialty)
            options = options_generator(objects_list)

        if selector.get('block_id') == 'block-contest':
            sprint = Sprint.objects.get(id=blocks['sprint'])
            objects_list = sprint.contest.all()
            options = options_generator(objects_list)

        if selector.get('block_id') == 'block-problem':
            contest = Contest.objects.get(id=blocks['contest'])
            objects_list = contest.problem.all()
            options = options_generator(objects_list)

        if selector.get('block_id') == 'block-hint':
            problem = Problem.objects.get(id=blocks['problem'])
            objects_list = problem.hint.all()
            slack_id = selector['user']['id']
            options = options_generator(objects_list, slack_id=slack_id)

        if selector.get('block_id') == 'block-test':
            problem = Problem.objects.get(id=blocks['problem'])
            objects_list = problem.test.all()
            options = options_generator(objects_list)

        return JsonResponse({"options": options}, safe=False)


def user_registration(payload):
    """Вывод формы регистрации, валидация и добавление пользователя в базу"""
    slack_id = payload['user']['id']
    if Student.objects.filter(slack_id=slack_id).exists():
        channel = payload['channel']['id']
        text = f'Мы уже знакомы, <@{slack_id}>!'
        client.chat_postMessage(channel=channel, text=text)
        return HttpResponse(status=200)

    if payload['type'] == 'block_actions':
        client.views_open(trigger_id=payload['trigger_id'],
                          view=json.dumps(register_form))
        return HttpResponse(status=200)

    data = payload['view']['state']['values']
    first_name = data['first_name']['0']['value']
    last_name = data['last_name']['0']['value']
    email = data['email']['0']['value']
    cohort = data['cohort']['0']['value']
    specialty = data['specialty']['0']['selected_option']['value']
    specialty = Specialty.objects.get(pk=specialty)
    user = Student(first_name=first_name, last_name=last_name, email=email,
                   cohort=cohort, slack_id=slack_id, specialty=specialty)

    try:
        user.clean_fields()
        user.save()
        client.chat_postMessage(channel=f'@{slack_id}',
                                blocks=user_greeting(slack_id))
        return HttpResponse(status=200)

    except ValidationError as e:
        errors = e.message_dict
        response = validation_generator(errors)
        return JsonResponse(response, safe=False)
