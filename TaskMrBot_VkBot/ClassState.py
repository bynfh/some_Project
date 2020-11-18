from vk_api.keyboard import VkKeyboard, VkKeyboardColor
class State():

    def __init__(self, Message, TypesProduct, PhotoProduct, Keyboard=[]):
        self.Message = Message
        self.TypesProduct = TypesProduct
        self.PhotoProduct = PhotoProduct
        self.Keyboard = Keyboard

    def GetStateProduct(self):
        try:
            Message = self.Message
            Photo = self.PhotoProduct
            if isinstance(Photo, dict):
                attachment = ','.join(Photo.values())
            elif isinstance(Photo, str):
                attachment = Photo
            else:
                attachment = ''
        except AttributeError:
            Message = f'Раздел {self.TypesProduct} настроен не до конца'
            attachment = ''
        keyboard = VkKeyboard(one_time=True)
        if self.Keyboard:
            for button in self.Keyboard:
                if button.lower() == 'назад':
                    keyboard.add_button(button, color=VkKeyboardColor.SECONDARY)
                else:
                    keyboard.add_button(button, color=VkKeyboardColor.POSITIVE)
        else:
            keyboard.add_button('Меню', color=VkKeyboardColor.POSITIVE)
        return Message, keyboard, attachment


