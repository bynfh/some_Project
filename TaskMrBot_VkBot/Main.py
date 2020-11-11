import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import random


def write_msg(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, "random_id": get_random_id(), "keyboard" : keyboard.get_keyboard()})


# API-ключ созданный ранее
token = "3fcfee483ffadcf5ea28be5aed479775c65e2554ec8cfe08ac73ae0ffa10077048b930d99c4a7e41ea7b2"

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня( то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text.lower()
            keyboard = VkKeyboard(one_time=True)

            keyboard.add_button('Булочки', color=VkKeyboardColor.SECONDARY)
            keyboard.add_button('Пицца', color=VkKeyboardColor.POSITIVE)
            # Каменная логика ответа
            if request == "привет":
                write_msg(event.user_id, "тест", keyboard)
            elif request == "булочки":
                write_msg(event.user_id, "сама как булочка", keyboard)
            else:
                write_msg(event.user_id, "Пиццу хочешь?", keyboard)