import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from loguru import logger
import sqlite3

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
                yield from Cake()
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
    PhotoBread = {
                   'белый хлеб': 'photo-200208378_457239027',
                   'ржаной хлеб': 'photo-200208378_457239026',
                  }
    attachment = ','.join(PhotoBread.values())
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
    yield from SingleBread(answer, PhotoBread.get(answer))

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
    Message = '''Вы перешли в раздел Пицца. В нашем меню:
                 1)Маргарита
                 2)Пепперони
                 3)Баварская
                 Выберите продукт'''
    keyboard = VkKeyboard(one_time=True)
    PizzaTypes = GetProductsFromDB('пицца')
    PhotoPizzes = {
                   'маргарита': 'photo-200208378_457239025',
                   'пепперони': 'photo-200208378_457239024',
                   'баварская': 'photo-200208378_457239023',
                  }
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
    yield from SinglePizza(answer, PhotoPizzes.get(answer))

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
    Message = '''Вы перешли в раздел Пироги. В нашем меню:
                     1)Мясной
                     2)Рыбник
                     3)Капустный
                     Выберите продукт'''
    keyboard = VkKeyboard(one_time=True)
    CakeTypes = GetProductsFromDB('пироги')
    PhotoCake = {
                  'мясной пирог': 'photo-200208378_457239022',
                  'рыбник': 'photo-200208378_457239020',
                  'капустный пирог': 'photo-200208378_457239021',
                }
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
    yield from SingleCake(answer, PhotoCake.get(answer))


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
