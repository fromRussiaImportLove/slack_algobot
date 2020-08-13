

def options_generator(objects_list):
    '''Генератор списка опций. На вход принимает QuerySet из объектов.
    Возвращает массив из набора опций'''
    options = []
    for item in objects_list:
        option = {
            "text": {
                "type": "plain_text",
                "text": str(item)
            },
            "value": str(item.pk)
        }
        options.append(option)
    return options


def validation_generator(errors):
    '''Составляет словарь ошибок валидации для json ответа в слак'''
    for key in errors:
        errors[key] = ' '.join(errors[key])
    response = {
        "response_action": "errors",
        "errors": errors
        }
    return response
