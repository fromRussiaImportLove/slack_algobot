from .models import Sprint, Contest, Problem, Hint, Student
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
    }

    def __call__(self, payload=None):
        if payload:
            logger.info('in class, we are ###', payload)
            if payload.get('user'):
                self.user = Student.objects.get(slack_id=payload['user']['id'])
                spec = self.user.specialty
            if payload['actions'][0]['block_id'] == 'useractionblock':
                return self.build_sprint()
            if payload['actions'][0]['block_id'] == 'block-sprint':
                sprint_id = payload['actions'][0]['selected_option']['value']
                return self.build_contest(sprint_id)
            if payload['actions'][0]['block_id'] == 'block-contest':
                contest_id = payload['actions'][0]['selected_option']['value']
                return self.build_problem(contest_id)
            if payload['actions'][0]['block_id'] == 'block-problem':
                problem_id = payload['actions'][0]['selected_option']['value']
                return self.build_hint(problem_id)

            raise Exception('not avilaible blocks in payload')
        raise Exception('payload is need')

    def build_sprint(self):
        '''Строим спринты'''
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

    def build_hint(self, problem_id):
        problem = Problem.objects.get(id=problem_id)
        contest = problem.contest
        sprint = contest.sprint.get(specialty=self.user.specialty)
        problems = contest.problem.all()
        contests = sprint.contest.all()
        sprints = Sprint.objects.all()
        hints = problem.hint.all()

        blocks = [
            self.build_block(sprints, sprint),
            self.build_block(contests, contest),
            self.build_block(problems, problem),
            self.build_block(hints)
        ]

        return self.build_view(blocks)

    def get_model(self, section):
        models = {
            'sprint': Sprint,
            'contest': Contest,
            'problem': Problem,
            'hint': Hint
        }

        return models[section]

    def build_block(self, queryset, init=None):
        """
        Строит блок для формы
        :param queryset: набор объектов для выпадающего меню соотв. типа (спринт, контест, задача)
        :param init: номер изначально выбранного объекта
        :return: словарь с блоком
        """

        section = queryset.model._meta.model_name
        section_type = 'input' if section == 'hint' else 'section'

        block = {
                "block_id": f'block-{section}',
                "type": section_type,
        }

        elems = {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": self.TEXT_GET_ITEM[section],
                    },
                    "options": [{"text": {"type": "plain_text", "text": f"{obj}"},
                                 "value": f"{obj.id}"} for obj in queryset]
                }

        if section_type == 'section':
            logger.info(elems)
            block["accessory"] = elems
            block["text"] = {
                    "type": 'mrkdwn',
                    "text": f'{section}'
                }

        if section_type == 'input':
            block["element"] = elems
            block["element"]["action_id"] = 'get-hint-complete'
            block["label"] = {
                    "type": "plain_text",
                    "text": f'{section}',
                }

        if init:
            # init = self.get_model(section).objects.get(id=init)
            block["accessory"]["initial_option"] = {
                "text": {"type": "plain_text", "text": f"{init}"},
                "value": f"{init.id}"
            }

        return block

    def build_view(self, blocks):

        view = {
            "callback_id": self.CALLBACK_ID,
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": self.TEXT_TITLE,
            },
            "submit": {
                "type": "plain_text",
                "text": self.TEXT_SUBMIT,
            },
            "close": {
                "type": "plain_text",
                "text": self.TEXT_CLOSE,
            },
            "blocks": blocks
        }

        return json.dumps(view)
