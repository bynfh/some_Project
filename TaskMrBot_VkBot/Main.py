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

def GetProductsFromDB(section):
    with sqlite3.connect('VkBot.db') as Connection:
        cursor = Connection.cursor()
        ListWithSection = []
        for row in cursor.execute(f'''SELECT prod.name
                                      FROM product prod,
                                           section sec
                                      WHERE sec.ID_section = prod.ID_section
                                      AND   sec.name = "{section.lower()}"'''):
            ListWithSection.append(row[0])
        return ListWithSection

def section():
    '''Функция-генератор. Создает 3 кнопки - разделы и одна кнопку - назад.
       Прикладывается 3 вложения в виде картинок
       Ответ который дает пользователь от этого зависит в какое следующее
       состояние перейдем.'''
    while True:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('Хлеб', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Пицца', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Пироги', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        attachment = 'photo-200208378_457239017,' \
                     'photo-200208378_457239019,' \
                     'photo-200208378_457239018'

        answer = yield "Добрый день! Что хотите заказать? \n" \
                       "Это будет только что из печи, хрустящий хлеб?\n" \
                       "Может это будет пицца прямиком из Италии?\n" \
                       "Или вы хотите отведать вкусный, домашний пирог?\n", keyboard, attachment

        section = answer.lower()
        if section in GetSectionFromDB():
            if section == 'хлеб':
                yield from Bread()
            if section == 'пицца':
                yield from Pizza()
            if section == 'пироги':
                yield from Cacke()
            if section == 'назад':
                yield from section()

def Bread():
    '''Функция-генератор. Создает столько кнопок, сколько позиций хлеба в БД + кнопка назад.
       Прикладывается два вложения в виде картинок
       состояние перейдем.'''
    Message = '''Вы перешли в раздел Хлеб. 
                 В нашем ассортименте:    
                     1)Белый хлеб
                     2)Ржаной хлеб
                 Выберите продукт'''
    attachment = 'photo-200208378_457239027,' \
                 'photo-200208378_457239026'
#Добавляем кол-во кнопок сколько позиций в БД + назад
    BreadTypes = GetProductsFromDB('хлеб')
    keyboard = VkKeyboard(one_time=True)
    for BreadType in BreadTypes:
        keyboard.add_button(BreadType, color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)

    answer = yield Message, keyboard, attachment

    BreadTypes = list(map(str.lower, BreadTypes))
    if answer == 'назад':
        yield from section()
    while answer not in BreadTypes:
        answer = yield "Выберите достпуный продукт", keyboard, attachment
        if answer == 'назад':
            yield from section()
#Переходы в следущие состояния
    if answer == 'белый хлеб':
        yield from WhiteBread()
    if answer == 'ржаной хлеб':
        yield from BrownBread()

def WhiteBread():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239027'
    answer = yield f"Вы заказали в разделе Хлеб. Товар: Белый хлеб. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Bread()

def BrownBread():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239026'
    answer = yield f"Вы заказали в разделе Хлеб. Товар: Ржаной хлеб. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Bread()


def Pizza():
    Message = '''Вы перешли в раздел Пицца. В нашем меню:
                 1)Маргарита
                 2)Пепперони
                 3)Баварская
                 Выберите продукт'''
    keyboard = VkKeyboard(one_time=True)
    PizzaTypes = GetProductsFromDB('пицца')
    attachment = 'photo-200208378_457239025,' \
                 'photo-200208378_457239024,' \
                 'photo-200208378_457239023'
    for PizzaType in PizzaTypes:
        keyboard.add_button(PizzaType, color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
    answer = yield Message, keyboard, attachment
    PizzaTypes = list(map(str.lower, PizzaTypes))
    if answer == 'назад':
        yield from section()
    while answer not in PizzaTypes:
        answer = yield "Выберите достпуный продукт", keyboard, attachment
        if answer == 'назад':
            yield from section()
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.SECONDARY)
    if answer == 'маргарита':
        yield from MargaritaPizz()
    if answer == 'пепперони':
        yield from PepperoniPizz()
    if answer == 'баварская':
        yield from BavarskayaPizz()

def MargaritaPizz():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239025'
    answer = yield f"Вы заказали в разделе Пицца. Товар: Маргарита. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Pizza()

def PepperoniPizz():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239024'
    answer = yield f"Вы заказали в разделе Пицца. Товар: Пеперони. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Pizza()


def BavarskayaPizz():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239023'
    answer = yield f"Вы заказали в разделе Пицца. Товар: Баварская. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Pizza()


def Cacke():
    Message = '''Вы перешли в раздел Пироги. В нашем меню:
                     1)Мясной
                     2)Рыбник
                     3)Капустный
                     Выберите продукт'''
    keyboard = VkKeyboard(one_time=True)
    CackeTypes = GetProductsFromDB('пироги')
    attachment = 'photo-200208378_457239020,' \
                 'photo-200208378_457239022,' \
                 'photo-200208378_457239021'
    for CackeType in CackeTypes:
        keyboard.add_button(CackeType, color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
    answer = yield Message, keyboard, attachment
    CackeTypes = list(map(str.lower, CackeTypes))
    if answer == 'назад':
        yield from section()
    while answer not in CackeTypes:
        answer = yield "Выберите достпуный продукт", keyboard, attachment
        if answer == 'назад':
            yield from section()
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.SECONDARY)
    if answer == 'рыбник':
        yield from FishCake()
    if answer == 'мясной пирог':
        yield from MeatCake()
    if answer == 'капустный пирог':
        yield from CabbegeCake()

def MeatCake():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239022'
    answer = yield f"Вы заказали в разделе Пироги. Товар: Мясной пирог. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Cacke()

def FishCake():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239020'
    answer = yield f"Вы заказали в разделе Пироги. Товар: Рыбник. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Cacke()

def CabbegeCake():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = 'photo-200208378_457239021'
    answer = yield f"Вы заказали в разделе Пироги. Товар: Капустный пирог. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Cacke()


def write_msg(vk, event, user_id, message, keyboard, attachment):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': get_random_id(),
                                'keyboard': keyboard.get_keyboard(),
                                'attachment':attachment,})
    logger.debug(f"Message for user_ID:[{event.user_id}]:{message}")


def main():
    token = "3fcfee483ffadcf5ea28be5aed479775c65e2554ec8cfe08ac73ae0ffa10077048b930d99c4a7e41ea7b2"
    # Авторизуемся как сообщество
    vk = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk)

    GenForEachUser_id = {}
    for event in longpoll.listen():
        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
            # Если оно имеет метку для меня( то есть бота)
            if event.to_me:
                logger.debug(f"We received new message. TEXT:[{event.text.lower()}] ID:[{event.user_id}]")

                if event.user_id not in GenForEachUser_id.keys():
                    DialogGenerator = section()
                    SetupGenerator = next(DialogGenerator)
                    GenForEachUser_id[event.user_id] = DialogGenerator
                    write_msg(vk, event, event.user_id, SetupGenerator[0], SetupGenerator[1], SetupGenerator[2])
                    logger.debug(f"Added new generator for user. ID:[{event.user_id}]")
                    continue

                # Сообщение от пользователя
                request = event.text.lower()
                message, keybord, attachment = GenForEachUser_id[event.user_id].send(request)
                write_msg(vk, event, event.user_id, message, keybord, attachment)


if __name__ == "__main__":
    try:
        logger.info("Programm started")
        main()
    except KeyboardInterrupt:
        logger.error("You stopped program")
