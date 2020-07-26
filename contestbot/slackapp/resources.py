dialog_plot = {
    "title": "Давай знакомится",
    "submit_label": "Отправить",
    "callback_id": "register_form",
    "elements": [

        {
            "type": "text",
            "label": "Имя",
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
    "image_url": "https://klike.net/uploads/posts/2019-07/1564314090_3.jpg", 
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
    },]
},

]

cat = [{
    "type": "actions", 
    "block_id": "actionblock7891",
    
    "elements": [{
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Хочу котика"
        },
        "value": "click_me_1234",
        "action_id": "button",
        "style": "danger",
    },]
},
{
  "type": "context",
  "elements": [
   
    {
      "type": "mrkdwn",
      "text": "Для того чтобы получить тест, необходимо пойти авторизацию - команда */register*\nПосле авторизации Вы сможите запросить исходные данные тестов - команда */getfile (тест)*\nЕсли просто хотите погладить котика, жмите кнопку)\nСтавь :+1: если прочитал."
    }
  ]
}
]