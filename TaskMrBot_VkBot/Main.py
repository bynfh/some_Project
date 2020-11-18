import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from loguru import logger
import sqlite3
import Bot_config
from ClassState import State

logger.add("VkBot_Bakery.json",
           format="{time:D-M-YY  HH:mm} {level} {message}",
           level="DEBUG",
           serialize=True,)

def GetSectionFromDB():
    '''Достает ВСЕ разделы из БД из таблицы section'''
    with sqlite3.connect('VkBot.db') as Connection:
        cursor = Connection.cursor()
        ListWithSection = []
        for row in cursor.execute(f'''SELECT sec.name             
                                      FROM   section sec
                                      '''):
            ListWithSection.append(row[0].lower())
        return ListWithSection

def GetProductsFromDB(section):
    '''Достает ВСЕ продукты из таблицы product'''
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


def GetSecOnProductFromDB(product):
    '''Достает из БД Имя секции для конкретного продукта'''
    with sqlite3.connect('VkBot.db') as Connection:
        cursor = Connection.cursor()
        ListWithSection = []
        for row in cursor.execute(f'''SELECT sec.name
                                      FROM product prod,
                                           section sec
                                      WHERE sec.ID_section = prod.ID_section
                                      AND   lower(prod.name) = "{product.capitalize()}"'''):
            ListWithSection.append(row[0])
        return ListWithSection


States_t = {}
def StateStore(request):
    '''Функция для хранения состояний. Выдает предыдущее состояние для текущего'''
    States_t['меню'] = 'меню'
    request = request.lower()
    if request in States_t:
        logger.debug(f'BackState = {States_t[request]}')
        return States_t[request]
    else:
        Sections = GetSectionFromDB()
        for Section in Sections:
            States_t[Section.lower()] = 'меню'
        Products = GetProductsFromDB(request)
        for Product in Products:
            States_t[Product.lower()] = request
        if request not in States_t:
            Section = GetSecOnProductFromDB(request)[0]
            States_t[request.lower()] = Section
        logger.debug(f'BackState = {States_t[request]}')
        return States_t[request]


def write_msg(vk, event, user_id, message, keyboard, attachment):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': get_random_id(),
                                'keyboard': keyboard.get_keyboard(),
                                'attachment': attachment, })

def SetState():
    '''Создает объекты по каждой позиции в БД, на выходе словать с handlers'''
    Bread = State(Bot_config.MsgSectionBread,
                  GetProductsFromDB('хлеб'),
                  Bot_config.PhotoBread,
                  Bot_config.KeyboardBread,
                  )

    WhiteBread = State(Bot_config.MsgBread.get('белый хлеб'),
                       ['белый хлеб'],
                       Bot_config.PhotoBread.get('белый хлеб'),
                       Bot_config.KeyboardSingleProduct,
                       )

    BrownBread = State(Bot_config.MsgBread.get('ржаной хлеб'),
                       ['ржаной хлеб'],
                       Bot_config.PhotoBread.get('ржаной хлеб'),
                       Bot_config.KeyboardSingleProduct,
                       )
    Pizza = State(Bot_config.MsgSectionPizz,
                  GetProductsFromDB('пицца'),
                  Bot_config.PhotoPizzes,
                  Bot_config.KeyboardPizz,
                  )

    Margo = State(Bot_config.MsgPizz.get('маргарита'),
                  ['маргарита'],
                  Bot_config.PhotoPizzes.get('маргарита'),
                  Bot_config.KeyboardSingleProduct,
                  )

    Peper = State(Bot_config.MsgPizz.get('пепперони'),
                  ['пепперони'],
                  Bot_config.PhotoPizzes.get('пепперони'),
                  Bot_config.KeyboardSingleProduct,
                  )

    Bavar = State(Bot_config.MsgPizz.get('баварская'),
                  ['баварская'],
                  Bot_config.PhotoPizzes.get('баварская'),
                  Bot_config.KeyboardSingleProduct,
                  )

    Cake = State(Bot_config.MsgSectionCake,
                 GetProductsFromDB('пироги'),
                 Bot_config.PhotoCake,
                 Bot_config.KeyboardCake)

    Meat = State(Bot_config.MsgCake.get('мясной пирог'),
                 ['мясной пирог'],
                 Bot_config.PhotoCake.get('мясной пирог'),
                 Bot_config.KeyboardSingleProduct,
                 )

    Fish = State(Bot_config.MsgCake.get('рыбник'),
                 ['рыбник'],
                 Bot_config.PhotoCake.get('рыбник'),
                 Bot_config.KeyboardSingleProduct,
                 )

    Cabbag = State(Bot_config.MsgCake.get('капустный пирог'),
                   ['капустный пирог'],
                   Bot_config.PhotoCake.get('капустный пирог'),
                   Bot_config.KeyboardSingleProduct,
                   )

    Start = State(Bot_config.MsgStart,
                  GetSectionFromDB(),
                  Bot_config.PhotoStart,
                  Bot_config.KeyboardStart)

    Handlers = {'меню': Start.GetObject(),
                'хлеб': Bread.GetObject(),
                'белый хлеб': WhiteBread.GetObject(),
                'ржаной хлеб': BrownBread.GetObject(),
                'пицца': Pizza.GetObject(),
                'маргарита': Margo.GetObject(),
                'пепперони': Peper.GetObject(),
                'баварская': Bavar.GetObject(),
                'пироги': Cake.GetObject(),
                'мясной пирог': Meat.GetObject(),
                'рыбник': Fish.GetObject(),
                'капустный пирог': Cabbag.GetObject(),
                'назад': Start.GetObject(), }
    return Handlers


def main():
    StateForEachUsers = {}
    token = Bot_config.TOKEN
    vk = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
            # Если оно имеет метку для меня( то есть бота)
            if event.to_me:
                # Если для этого пользователя не созданы объекты, то создадим и запишем их в словарь
                if event.user_id not in StateForEachUsers.keys():
                    StateForEachUsers[event.user_id] = SetState()
                    logger.debug(f'We create new objects for ID:[{event.user_id}]')
                logger.debug(f"We received new message from ID:[{event.user_id}] TEXT:[{event.text.lower()}]")
                request = event.text.lower()

                if request not in StateForEachUsers[event.user_id]:
                    logger.debug(f'Request "{request}" not in Handlers')
                    message, keybord, attachment = StateForEachUsers[event.user_id].get('меню')
                    StateForEachUsers[event.user_id]['PreviousState'] = StateStore('меню')
                elif request == 'назад':
                    logger.debug(f'Request in "назад"')
                    back = StateForEachUsers[event.user_id]['PreviousState']
                    message, keybord, attachment = StateForEachUsers[event.user_id].get(back)
                    StateForEachUsers[event.user_id]['PreviousState'] = StateStore(back)
                else:
                    message, keybord, attachment = StateForEachUsers[event.user_id].get(request)
                    StateForEachUsers[event.user_id]['PreviousState'] = StateStore(request)

                write_msg(vk, event, event.user_id, message, keybord, attachment)


if __name__ == "__main__":
    try:
        logger.info("Programm started")
        main()
    except KeyboardInterrupt:
        logger.error("You stopped program")



