register_form = {  # Форма регистрации
    "callback_id": "register-form",
    "type": "modal",
    "title": {
        "type": "plain_text",
        "text": "Давай знакомиться",
    },
    "submit": {
        "type": "plain_text",
        "text": "Отправить",
    },
    "close": {
        "type": "plain_text",
        "text": "Отменить",
    },
    "blocks": [
        {
            "type": "input",
            "block_id": "first_name",
            "element": {
                "type": "plain_text_input",
                "action_id": "0",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Введи своё имя..."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Имя"
            }
        },
        {
            "type": "input",
            "block_id": "last_name",
            "element": {
                "type": "plain_text_input",
                "action_id": "0",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Введи свою фамилию..."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Фамилия"
            }
        },
        {
            "type": "input",
            "block_id": "email",
            "element": {
                "type": "plain_text_input",
                "action_id": "0",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Введи свой email..."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Почта в Контесте"
            }
        },
        {
            "type": "input",
            "block_id": "cohort",
            "element": {
                "type": "plain_text_input",
                "action_id": "0",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Введи номер своей когорты..."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Когорта"
            }
        },
        {
            "type": "input",
            "block_id": "specialty",
            "element": {
                "type": "external_select",
                "min_query_length": 0,
                "action_id": "0",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Выбери специальность..."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Специальность"
            }
        }
    ]
}

anonymous_greeting = [{  # Приветствие незарегистрированного пользователя
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": ("Привет, незнакомец! "
                 "Прежде чем попросить помощь "
                 "расскажи немного о себе. "
                 "Нажми на кнопку 'Зарегистрироваться'.")
        }
    },
    {
    "type": "actions",
    "block_id": "registerblock1",
    "elements": [{
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Зарегистрироваться"
        },
        "style": "primary",
        "value": "click_me_register"
        }
    ]
}]


def user_greeting(user):
    '''Приветствие зарегистрированного пользователя'''
    block = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (f"Привет, <@{user}>! "
                     "Ты можешь получить тест или подсказку к задаче. "
                     "Выбирай с умом!")
            }
        },
        {
        "type": "actions",
        "block_id": "useractionblock",
        "elements": [{
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Получить тест"
            },
            "style": "primary",
            "value": "click_me_test"
            },
            {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Получить подсказку"
            },
            "style": "primary",
            "value": "click_me_hint"
            }
        ]
    }]
    return block
