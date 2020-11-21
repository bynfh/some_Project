from rivescript import RiveScript
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from loguru import logger
#-------------------------GLOBAL VARIABLES---------------------------------------------------------
TOKEN = "3fcfee483ffadcf5ea28be5aed479775c65e2554ec8cfe08ac73ae0ffa10077048b930d99c4a7e41ea7b2"
path_bot = "./eg/brain"
#-------------------------GLOBAL VARIABLES---------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#----------------------------SET LOGGER------------------------------------------------------------
logger.add("./log/VkBot_Bakery.json",
           format="{time:D-M-YY  HH:mm} {level} {message}",
           level="INFO",
           serialize=True,)
#----------------------------SET LOGGER------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#----------------------------FUNCTIONS-------------------------------------------------------------
def write_msg(vk, event, user_id, message, attachment='', keyboard=False):
    '''Функция, отправляет сообщение для пользователя.
       Если keyboard = False, то клавитура пользователю не отправляется.'''
    if keyboard:
        vk.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'random_id': get_random_id(),
                                    'keyboard': keyboard.get_keyboard(),
                                    'attachment': attachment, })
    else:
        vk.method('messages.send', {'user_id': user_id,
                                    'message': message,
                                    'random_id': get_random_id(),
                                    'attachment': attachment, })
    logger.debug(f'ID:[{user_id}]. We sent:[MSG:{message}; ATTACH:{attachment}; KEYB:{keyboard}]')

def CreateNewBot(path):
    '''Для создания нового бота'''
    rs = RiveScript(utf8=True)
    rs.load_directory(path)
    rs.sort_replies()
    return rs

def CheckNeedKeyboard(reply):
    '''Возвращает клавиатуру, если она есть в ответе от бота.
       Если клавиатуры нет, возвращает False'''
    if reply.get('keyboard', '') != '':
        ListButtons = reply.get("keyboard").split(';')
        keyboard = VkKeyboard(one_time=True)
        for button in ListButtons:
            if button.lower() == 'назад':
                keyboard.add_button(button, color=VkKeyboardColor.SECONDARY)
            else:
                keyboard.add_button(button, color=VkKeyboardColor.POSITIVE)

    else:
        keyboard = False
    return keyboard


def start(TOKEN, path_bot):
    logger.debug('Block start has been lunched')
    BotForEachUser = {}
    vk = vk_api.VkApi(token=TOKEN)
    longpoll = VkLongPoll(vk)
    logger.debug('Authorization VK_BOT successfully')
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                # Создание личного бота для каждого пользователя
                if event.user_id not in BotForEachUser.keys():
                    BotForEachUser[event.user_id] = CreateNewBot(path_bot)
                    logger.debug(f'ID:[{event.user_id}] We create new bot')
                # Получаем ответ от бота, для конкретного пользователя
                logger.debug(f'ID [{event.user_id}] Text received:[{event.text.lower()}]')
                reply = BotForEachUser[event.user_id].reply("bakery_bot", event.text.lower())
                logger.debug(f'ID:[{event.user_id}] From bot reply: [{reply}]')
                try:
                    try:
                        reply = json.loads(reply)
                        logger.debug(f'ID:[{event.user_id}]. Reply  convert to dict success')
                    except json.decoder.JSONDecodeError:
                        pass
                    # Когда в ответе от бота не словарь, а строка
                    if isinstance(reply, dict):
                        attachment = reply.get("photo", "").replace(';', ',')
                    else:
                        logger.error(f'ID:[{event.user_id}]. Reply from bot is not dict: {reply}')
                        write_msg(vk, event, event.user_id, reply)
                        continue
                    keyboard = CheckNeedKeyboard(reply)
                    write_msg(vk, event, event.user_id, reply.get("msg", ""), attachment, keyboard)
                except:
                    logger.exception("ID:[{event.user_id}]. SOMETHING WRONG")
#----------------------------FUNCTIONS-------------------------------------------------------------
if __name__ == '__main__':
    try:
        start(TOKEN=TOKEN,
              path_bot=path_bot)
    except KeyboardInterrupt:
        logger.error(f'You stopped programm CTR+C')
    except Exception as error:
        logger.exception(f'Bot stopped, but reason is unknown')


