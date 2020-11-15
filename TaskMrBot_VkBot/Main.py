import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from loguru import logger
import sqlite3
import Bot_config

logger.add("VkBot_Bakery.json",
           format="{time:D-M-YY  HH:mm} {level} {message}",
           level="DEBUG",
           serialize=True,)

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

def section(Handlers=None):
    '''Функция-генератор. Создает 3 кнопки - разделы и одна кнопку - назад.
       Прикладывается 3 вложения в виде картинок
       Ответ который дает пользователь от этого зависит в какое следующее
       состояние перейдем.'''
    while True:
        Handlers = {'хлеб': Bread(),
                    'пироги': Cake(),
                    'пицца': Pizza(), }

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        SectionsFromDB = GetSectionFromDB()
        for Section in SectionsFromDB:
            keyboard.add_button(Section.capitalize(), color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        try:
            attachment = Bot_config.PhotoForStart
            message = Bot_config.MessegeForStart
        except AttributeError:
            attachment = ''
            message = 'Администратор не добавил сообщение для старта'
            logger.error('Заполните Bot_config.MessegeForStart or Bot_config.PhotoForStart')

        Response = yield message, keyboard, attachment

        Section = Response.lower()
        if Section in SectionsFromDB:
            try:
                yield from Handlers.get(Section)
            except TypeError:
                logger.error(f'Тема {Section.capitalize()} есть в БД но обработчика нет')
                yield f'Раздел {Section.capitalize()} не доработан. Попробуйте что-то другое', keyboard, ''

def Bread():
    '''Функция-генератор. Создает столько кнопок, сколько позиций хлеба в БД + кнопка назад.
       Прикладывается два вложения в виде картинок
       состояние перейдем.'''
    try:
        Message = Bot_config.MessageSectionBread
        Photo = Bot_config.PhotoBread
        attachment = ','.join(Photo.values())
    except AttributeError:
        Message = 'Для раздела Хлеб нет администратор не добавил сообщение'
        attachment = ''
        logger.error('Заполните Bot_config.MessageSectionBread or Bot_config.PhotoBread')
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
    yield from SingleBread(answer, Bot_config.PhotoBread.get(answer))

def SingleBread(TypeBread, Photo):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = Photo
    answer = yield f"Вы заказали в разделе Пицца." \
                   f" Товар: {TypeBread.capitalize()}. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Bread()


def Pizza():
    Message = Bot_config.MessageSectionPizz
    keyboard = VkKeyboard(one_time=True)
    PizzaTypes = GetProductsFromDB('пицца')
    PhotoPizzes = Bot_config.PhotoPizzes
    attachment = ','.join(PhotoPizzes.values())
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
    yield from SingleBread(answer, Bot_config.PhotoPizzes.get(answer))

def SinglePizza(TypePizza, Photo):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = Photo
    answer = yield f"Вы заказали в разделе Пицца." \
                   f" Товар: {TypePizza.capitalize()}. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Pizza()

def Cake():
    Message = Bot_config.MessageSectionCake
    keyboard = VkKeyboard(one_time=True)
    CakeTypes = GetProductsFromDB('пироги')
    PhotoCake = Bot_config.PhotoCake
    attachment = ','.join(PhotoCake.values())
    for CakeType in CakeTypes:
        keyboard.add_button(CakeType, color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
    answer = yield Message, keyboard, attachment
    CakeTypes = list(map(str.lower, CakeTypes))
    if answer == 'назад':
        yield from section()
    while answer not in CakeTypes:
        answer = yield "Выберите достпуный продукт", keyboard, attachment
        if answer == 'назад':
            yield from section()
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.SECONDARY)
    yield from SingleBread(answer, Bot_config.PhotoCake.get(answer))


def SingleCake(TypeCake, Photo):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать покупки', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    attachment = Photo
    answer = yield f"Вы заказали в разделе Пицца." \
                   f" Товар: {TypeCake.capitalize()}. Приятного аппетита", keyboard, attachment
    if answer == 'начать покупки':
        yield from section()
    if answer == 'назад':
        yield from Cake()


def write_msg(vk, event, user_id, message, keyboard, attachment):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': get_random_id(),
                                'keyboard': keyboard.get_keyboard(),
                                'attachment': attachment,})
    logger.debug(f"Message for user_ID:[{event.user_id}]:{message}")


def main():
    token = Bot_config.TOKEN
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
                    write_msg(vk, event, event.user_id, message=SetupGenerator[0],
                                                        keyboard=SetupGenerator[1],
                                                        attachment=SetupGenerator[2]
                              )
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
