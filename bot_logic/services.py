

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
