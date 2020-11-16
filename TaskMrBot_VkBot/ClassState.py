from vk_api.keyboard import VkKeyboard, VkKeyboardColor
class State():

    def __init__(self, Message, TypesProduct, PhotoProduct):
        self.Message = Message
        self.TypesProduct = TypesProduct
        self.PhotoProduct = PhotoProduct

    def GetStateProduct(self):
        try:
            Message = self.Message
            Photo = self.PhotoProduct
            attachment = ','.join(Photo.values())
        except AttributeError:
            Message = 'Для раздела Хлеб администратор не добавил сообщение'
            attachment = ''
        # Добавляем кол-во кнопок сколько позиций в БД + назад
        TypesProduct = self.TypesProduct
        keyboard = VkKeyboard(one_time=True)
        for BreadType in TypesProduct:
            keyboard.add_button(BreadType, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        return Message, keyboard, attachment

    def Start(self):
        Message = self.Message
        attachment = self.PhotoProduct
        # Добавляем кол-во кнопок сколько позиций в БД + назад
        TypesProduct = self.TypesProduct
        keyboard = VkKeyboard(one_time=True)
        for BreadType in TypesProduct:
            keyboard.add_button(BreadType, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        return Message, keyboard, attachment


