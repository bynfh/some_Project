import sys
def dialog():
    while True:
        answer = yield "Здравствуйте! Меня забыли наградить именем, а как зовут вас?"
        # убираем ведущие знаки пунктуации, оставляем только
        # первую компоненту имени, пишем её с заглавной буквы
        name = answer
        likes_python = yield from ask_yes_or_no("Приятно познакомиться, %s. Вам нравится Питон?" % name)
        if likes_python:
            answer = yield from discuss_good_python(name)
        else:
            answer = yield from discuss_bad_python(name)


def ask_yes_or_no(question):
    """Спросить вопрос и дождаться ответа, содержащего «да» или «нет».

    Возвращает:
        bool
    """
    answer = yield question
    while not ("да" in answer.lower() or "нет" in answer.lower()):
        answer = yield "Так да или нет?"
    return "да" in answer.lower()


def discuss_good_python(name):
    answer = yield "Мы с вами, %s, поразительно похожи! Что вам нравится в нём больше всего?" % name
    likes_article = yield from ask_yes_or_no("Ага. А как вам, кстати, статья на Хабре? Понравилась?")
    if likes_article:
        answer = yield "Чудно!"
    else:
        answer = yield "Жалко."
    return answer


def discuss_bad_python(name):
    answer = yield "Ай-яй-яй. %s, фу таким быть! Что именно вам так не нравится?" % name
    likes_article = yield from ask_yes_or_no(
        "Ваша позиция имеет право на существование. Статья "
        "на Хабре вам, надо полагать, тоже не понравилась?")
    if likes_article:
        answer = yield "Ну и ладно."
    else:
        answer = yield "Что «нет»? «Нет, не понравилась» или «нет, понравилась»?"
        answer = yield "Спокойно, это у меня юмор такой."
    return answer

g = dialog()
print(next(g))
while True:
    try:
        print(g.send(str(input('Введите сообщение для бота:'))))
    except KeyboardInterrupt:
        print('Вы завершили программу')
        sys.exit()
