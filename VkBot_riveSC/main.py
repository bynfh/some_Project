from rivescript import RiveScript
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import re
from loguru import logger
logger.add("VkBot_Bakery.json",
           format="{time:D-M-YY  HH:mm} {level} {message}",
           level="DEBUG",
           serialize=True,)
BotForEachUser = {}

def write_msg(vk, event, user_id, message, attachment='', keyboard=False):
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

TOKEN = "3fcfee483ffadcf5ea28be5aed479775c65e2554ec8cfe08ac73ae0ffa10077048b930d99c4a7e41ea7b2"
vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:
        # Если оно имеет метку для меня( то есть бота)
        if event.to_me:
            if event.user_id not in BotForEachUser.keys():
                rs = RiveScript(utf8=True)
                rs.load_directory("./eg/brain")
                rs.sort_replies()
                BotForEachUser[event.user_id] = rs
                logger.debug(f'We create new objects for ID:[{event.user_id}]')
            keyboard = False
            reply = BotForEachUser[event.user_id].reply("localuser", event.text.lower())
            try:
                try:
                    reply = json.loads(reply)
                except json.decoder.JSONDecodeError:
                    pass
                try:
                    attachment = reply.get("photo", "").replace(';', ',')
                except:
                    logger.error(f'Need check myself.rive because')
                    write_msg(vk, event, event.user_id, reply)
                    continue
                if reply.get('keyboard', '') != '':
                    ListButtons = reply.get("keyboard").split(';')
                    keyboard = VkKeyboard(one_time=True)
                    for button in ListButtons:
                        if button.lower() == 'назад':
                            keyboard.add_button(button, color=VkKeyboardColor.SECONDARY)
                        else:
                            keyboard.add_button(button, color=VkKeyboardColor.POSITIVE)

                write_msg(vk, event, event.user_id, reply.get("msg", ""), attachment, keyboard)
            except:
                logger.exception("SOMETHING WRONG")


