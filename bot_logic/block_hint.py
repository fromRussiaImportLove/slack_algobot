from .models import Sprint, Contest, Problem, Hint, Student, Test
from logging import getLogger
import json

logger = getLogger(__name__)


class GetHintForm():
    CALLBACK_ID = 'get-hint-form'
    TEXT_TITLE = 'Выберите задачу'
    TEXT_SUBMIT = 'Отправить'
    TEXT_CLOSE = 'Отменить'
    TEXT_GET_ITEM = {
        'sprint': 'Выберите спринт',
        'contest': 'Выберите контест',
        'problem': 'Выберите задачу',
        'hint': 'Доступные подсказки',
        'test': 'Доступные тесты'
    }

    def __call__(self, payload=None):
        """
        Вызов объекта класса, который принимает payload.
        По пути разбирает какой-именно блок запрашивается и перенаправляет вызов на
        внешний ввод (external_input), чтобы получить набор опций (объекты в раскр. списке)
        Логика выбора построения блока: если на входе первоначальный блок, значит строим спринты
        Если на входе блок с построенным спринтом, значит надо строить контесты и тд.

        На выходе возвращает json, на основе которого рисуется форма.

        :param payload: response from slack
        :return: json
        """

        if payload:
            if payload.get('user'):
                self.user = Student.objects.get(
                    slack_id=payload['user']['id'])

            if payload['actions'][0]['block_id'] == 'useractionblock':
                if payload['actions'][0]['value'] == 'click_me_test':
                    self.test_or_hint = 'test'
                if payload['actions'][0]['value'] == 'click_me_hint':
                    self.test_or_hint = 'hint'
                return self.build_sprint()

            if payload['actions'][0]['block_id'] == 'block-sprint':
                sprint_id = payload['actions'][0]['selected_option']['value']
                return self.build_contest(sprint_id)

            if payload['actions'][0]['block_id'] == 'block-contest':
                contest_id = payload['actions'][0]['selected_option']['value']
                return self.build_problem(contest_id)

            if payload['actions'][0]['block_id'] == 'block-problem':
                problem_id = payload['actions'][0]['selected_option']['value']
                return self.build_test_or_hint(problem_id)

            raise Exception('not avilaible blocks in payload')
        raise Exception('payload is need')

    def build_sprint(self):
        sprints = Sprint.objects.all()
        blocks = [self.build_block(sprints)]
        return self.build_view(blocks)

    def build_contest(self, sprint_id):
        sprints = Sprint.objects.all()
        sprint = Sprint.objects.get(id=sprint_id)
        contests = sprint.contest.all()
        blocks = [self.build_block(sprints, sprint),
                  self.build_block(contests)]
        return self.build_view(blocks)

    def build_problem(self, contest_id):
        sprints = Sprint.objects.filter(specialty=self.user.specialty)
        contest = Contest.objects.get(id=contest_id)
        sprint = contest.sprint.get(specialty=self.user.specialty)
        contests = sprint.contest.all()
        problems = contest.problem.all()

        blocks = [
            self.build_block(sprints, sprint),
            self.build_block(contests, contest),
            self.build_block(problems)
        ]
        return self.build_view(blocks)

    def build_test_or_hint(self, problem_id):
        problem = Problem.objects.get(id=problem_id)
        contest = problem.contest
        sprint = contest.sprint.get(specialty=self.user.specialty)
        problems = contest.problem.all()
        contests = sprint.contest.all()
        sprints = Sprint.objects.all()

        if self.test_or_hint == 'hint':
            tips = problem.hint.all()
        else:
            tips = problem.test.all()

        blocks = [
            self.build_block(sprints, sprint),
            self.build_block(contests, contest),
            self.build_block(problems, problem),
            self.build_block(tips)
        ]

        return self.build_view(blocks)

    def build_block(self, queryset, init=None):
        """
        Строит блок для формы
        :param queryset: набор объектов для выпадающего меню соотв. типа
        (спринт, контест, задача)
        :param init: изначально выбранный объект
        :return: словарь с блоком (block-object)
        """

        section = queryset.model._meta.model_name
        section_type = 'input' if section in ('hint', 'test') else 'section'

        block = {
            "block_id": f'block-{section}',
            "type": section_type,
        }

        elems = {
            "type": "external_select",
            "min_query_length": 0,
            "action_id": "0",
            "placeholder": {
                    "type": "plain_text",
                    "text": self.TEXT_GET_ITEM[section]
            },
        }

        if section_type == 'section':
            block["accessory"] = elems
            block["text"] = {
                "type": 'mrkdwn',
                "text": f'{section}'
            }

        if section_type == 'input':
            block["element"] = elems
            block["element"]["action_id"] = 'get-form-tips-complete'
            block["label"] = {
                "type": "plain_text",
                "text": f'{section}',
            }

        if init:
            block["accessory"]["initial_option"] = {
                "text": {"type": "plain_text", "text": f"{init}"},
                "value": f"{init.id}"
            }

        return block

    
    def build_view(self, blocks):
        TEXT_TYPE_FORM = 'Подказка: ' if self.test_or_hint == 'hint' else 'Тест: '

        view = {
            "callback_id": self.CALLBACK_ID,
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": TEXT_TYPE_FORM + self.TEXT_TITLE,
            },
            "close": {
                "type": "plain_text",
                "text": self.TEXT_CLOSE,
            },
            "blocks": blocks
        }
        if blocks[-1]['block_id'] in ('block-hint', 'block-test'):
            view["submit"] = {
                "type": "plain_text",
                "text": self.TEXT_SUBMIT,
            }
        return json.dumps(view)
