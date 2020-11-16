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

PriviousState = ['старт','старт']
def StateStore(state):
    if state != PriviousState[1]:
        PriviousState.append(state)
    if len(PriviousState) > 2:
        del PriviousState[0]
    return PriviousState[0]

def write_msg(vk, event, user_id, message, keyboard, attachment):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': get_random_id(),
                                'keyboard': keyboard.get_keyboard(),
                                'attachment': attachment,})
    logger.debug(f"Message for user_ID:[{event.user_id}]:{message}")


def main():
    Bread = State(Bot_config.MessageSectionBread, GetProductsFromDB('хлеб'), Bot_config.PhotoBread)
    WhiteBread = State(Bot_config.MessageBread.get('белый хлеб'), ['белый хлеб'], Bot_config.PhotoBread.get('белый хлеб'))
    BrownBread = State(Bot_config.MessageBread.get('ржаной хлеб'), ['ржаной хлеб'], Bot_config.PhotoBread.get('ржаной хлеб'))
    Pizza = State(Bot_config.MessageSectionPizz, GetProductsFromDB('пицца'), Bot_config.PhotoPizzes)
    Margo = State(Bot_config.MessagePizz.get('маргарита'), ['маргарита'], Bot_config.PhotoPizzes.get('маргарита'))
    Peper = State(Bot_config.MessagePizz.get('пепперони'), ['пепперони'], Bot_config.PhotoPizzes.get('пепперони'))
    Bavar = State(Bot_config.MessagePizz.get('баварская'), ['баварская'], Bot_config.PhotoPizzes.get('баварская'))
    Cake = State(Bot_config.MessageSectionCake, GetProductsFromDB('пироги'), Bot_config.PhotoCake)
    Meat = State(Bot_config.MessageCake.get('мясной'), ['мясной'], Bot_config.PhotoCake.get('мясной'))
    Fish = State(Bot_config.MessageCake.get('рыбник'), ['рыбник'], Bot_config.PhotoCake.get('рыбник'))
    Cabbag = State(Bot_config.MessageCake.get('капустный пирог'), ['капустный пирог'], Bot_config.PhotoCake.get('капустный пирог'))
    Start = State(Bot_config.MessegeForStart, GetSectionFromDB(), Bot_config.PhotoForStart)
    Handlers = {'старт': Start.GetStateProduct(),
                'хлеб': Bread.GetStateProduct(),
                'белый хлеб': WhiteBread.GetStateProduct(),
                'ржаной хлеб': BrownBread.GetStateProduct(),
                'пицца': Pizza.GetStateProduct(),
                'маргарита': Margo.GetStateProduct(),
                'пепперони': Peper.GetStateProduct(),
                'баварская': Bavar.GetStateProduct(),
                'пироги': Cake.GetStateProduct(),
                'мясной': Meat.GetStateProduct(),
                'рыбник': Fish.GetStateProduct(),
                'капустный пирог': Cabbag.GetStateProduct(),
                'назад': Start.GetStateProduct(),}

    token = Bot_config.TOKEN
    # Авторизуемся как сообщество
    vk = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk)
    store = ''
    for event in longpoll.listen():
        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
            # Если оно имеет метку для меня( то есть бота)
            if event.to_me:
                logger.debug(f"We received new message. TEXT:[{event.text.lower()}] ID:[{event.user_id}]")

                request = event.text.lower()

                try:
                    if request not in Handlers:
                        message, keybord, attachment = Handlers.get('старт')
                    elif request == 'назад':
                        message, keybord, attachment = Handlers.get(store)
                    else:
                        message, keybord, attachment = Handlers.get(request)
                except Exception as error:
                    message, keybord, attachment = Handlers.get('старт')


                store = StateStore(request)
                write_msg(vk, event, event.user_id, message, keybord, attachment)


if __name__ == "__main__":
    try:
        logger.info("Programm started")
        main()
    except KeyboardInterrupt:
        logger.error("You stopped program")
