dialog_plot = {
    "title": "Давай знакомится",
    "submit_label": "Отправить",
    "callback_id": "register_form",
    "elements": [

        {
            "type": "text",
            "label": "ФИО (полностью)",
            "name": "name"
        },

        {
            "type": "text",
            "label": "Почта в Контесте",
            "name": "email",

        },

        {
            "type": "text",
            "label": "Когорта",
            "name": "kogort",
            "value": 1
        },
    ]
}

photo_barsik = [{
    "image_url": "https://cdn23.img.ria.ru/images/148839/96/1488399659_0:0:960:960_600x0_80_0_1_e38b72053fffa5d3d7e82d2fe116f0b3.jpg",
    "text": "Барсик"
}]

barsik = [{
    "type": "actions",
    "block_id": "actionblock789",

    "elements": [{
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Погладить котика!"
        },
        "value": "click_me_123",
        "action_id": "button",
        "style": "primary",
    }, ]
},

]

cat = [{
    "type": "actions",
    "block_id": "actionblock7891",

    "elements": [{
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Получить тесты"
        },
        "value": "click_me_1234",
        "action_id": "button",
        "style": "danger",
    }, ]
},
    {
    "type": "context",
    "elements": [

        {
            "type": "mrkdwn",
            "text": "Для того чтобы получить тест, необходимо пойти авторизацию - команда */register*\nПосле авторизации Вы сможите запросить исходные данные тестов - команда */gettest (тест)* или подсказки - команда */gethint (подсказка)* *\nСтавь :+1: если прочитал."
        }
    ]
}
]


choose_your_destiny = [
    {
        "type": "section",
        "text": {
                "type": "plain_text",
                "text": "Привет! Чем могу помочь? Выбирай с умом",
        }
    },
    {
        "type": "actions",
        "block_id": "actionblock1",

        "elements": [

            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Хочу тест"
                },
                "value": "click_me_test",
                "action_id": "button1",
                "style": "danger",
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Хочу подсказку"
                },
                "value": "click_me_hint",
                "action_id": "button2",
                "style": "primary",
            },
        ],
    },

]


choose_test = {
    "title": "Выбери тест :)",
    "submit_label": "Отправить",
    "callback_id": "test_form",
    "elements": [

        {
            "type": "text",
            "label": "Номер спринта",
            "name": "sprint"
        },

        {
            "type": "text",
            "label": "Номер контекста",
            "name": "context",

        },

        {
            "type": "text",
            "label": "Название задачи",
            "name": "task",
            "value": 1
        },
        {
            "type": "text",
            "label": "Номер теста",
            "name": "test",
            "value": 1
        },
    ]
}


choose_hint = {
    "title": "Выбери подсказку :)",
    "submit_label": "Отправить",
    "callback_id": "prompt_form",
    "elements": [

        {
            "type": "text",
            "label": "Номер спринта",
            "name": "sprint"
        },

        {
            "type": "text",
            "label": "Номер контекста",
            "name": "context",

        },
        {
            "type": "text",
            "label": "Название задачи",
            "name": "task",
            "value": 1
        },
        {
            "type": "text",
            "label": "Номер подсказки",
            "name": "prompt",
            "value": 1
        },
    ]
}


def test_section(test):
    section = {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*Вы запросили данные:*\nСпринт: {test.problem.sprint_number}\nКонтест: {test.problem.contest_number}\nЗадача: {test.problem.title}"
            },
            {
                "type": "mrkdwn",
                "text": "*Доступные данные*\nОсталось подсказок · 3\nЧто еще тут вывести?"
            },

        ],

    },

    return section
