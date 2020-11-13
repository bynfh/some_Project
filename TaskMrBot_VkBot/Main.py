import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from loguru import logger
import sqlite3

logger.add("VkBot_Bakery.json",
           format="{time:D:M:YY  HH:mm} {level} {message}",
           level="DEBUG",
           serialize=True)


def GetSectionFromDB():
    with sqlite3.connect('VkBot.db') as Connection:

        cursor = Connection.cursor()

        ListWithSection = []
        for row in cursor.execute(f'''SELECT sec.name             
                                      FROM   section sec
                                      '''):
            ListWithSection.append(row[0].lower())

        return ListWithSection


def section():
    while True:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Хлеб', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('Пицца', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Пироги', color=VkKeyboardColor.POSITIVE)

        answer = yield "Добрый день! Что хотить закать?", keyboard
        # убираем ведущие знаки пунктуации, оставляем только
        # первую компоненту имени, пишем её с заглавной буквы

        section = answer.lower()
        if section in GetSectionFromDB():
            if section == 'хлеб':
                BreadStatus = yield from Bread(f"Вы перешли в раздел {section}. Выберите продукт")
            if section == 'пицца':
                PizzaStatus = yield from Pizza(f"Вы перешли в раздел {section}. Выберите продукт")
            if section == 'пироги':
                CackeStatus = yield from Cacke(f"Вы перешли в раздел {section}. Выберите продукт")


def Bread(question):
    """Спросить вопрос и дождаться ответа, содержащего «да» или «нет».

    Возвращает:
        bool
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Белый', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Ржаной', color=VkKeyboardColor.POSITIVE)
    answer = yield question, keyboard
    while not ("белый" in answer.lower() or "ржаной" in answer.lower()):
        answer = yield "Так какой?", keyboard
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.SECONDARY)
    yield f"Вы заказали в разделе Хлеб. Товар:{answer.lower()}", keyboard


def Pizza(name):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Белый', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Ржаной', color=VkKeyboardColor.POSITIVE)
    answer = yield question, keyboard
    while not ("белый" in answer.lower() or "ржаной" in answer.lower()):
        answer = yield "Так какой?", keyboard
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.SECONDARY)
    yield f"Вы заказали в разделе Хлеб. Товар:{answer.lower()}", keyboard


def Cacke(name):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Белый', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Ржаной', color=VkKeyboardColor.POSITIVE)
    answer = yield question, keyboard
    while not ("белый" in answer.lower() or "ржаной" in answer.lower()):
        answer = yield "Так какой?", keyboard
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.SECONDARY)
    yield f"Вы заказали в разделе Хлеб. Товар:{answer.lower()}", keyboard


def write_msg(vk, event, user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, "random_id": get_random_id(),
                                "keyboard": keyboard.get_keyboard()})
    logger.debug(f"Message for user_ID:[{event.user_id}]:{message}")


def main():
    # API-ключ созданный ранее
    token = "3fcfee483ffadcf5ea28be5aed479775c65e2554ec8cfe08ac73ae0ffa10077048b930d99c4a7e41ea7b2"

    # Авторизуемся как сообщество
    vk = vk_api.VkApi(token=token)

    # Работа с сообщениями
    longpoll = VkLongPoll(vk)

    ListWithGenerator = {}
    # Основной цикл
    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:

            # Если оно имеет метку для меня( то есть бота)
            if event.to_me:
                logger.debug(f"We received new message. TEXT:[{event.text.lower()}] ID:[{event.user_id}]")



                if event.user_id not in ListWithGenerator.keys():
                    DialogGenerator = section()
                    FirstHello = next(DialogGenerator)
                    ListWithGenerator[event.user_id] = DialogGenerator
                    write_msg(vk, event, event.user_id, FirstHello[0], FirstHello[1])
                    logger.debug(f"Added new generator for user. ID:[{event.user_id}]")
                    continue

                # Сообщение от пользователя
                request = event.text.lower()
                message, keybord = ListWithGenerator[event.user_id].send(request)
                write_msg(vk, event, event.user_id, message, keybord)


if __name__ == "__main__":
    main()
