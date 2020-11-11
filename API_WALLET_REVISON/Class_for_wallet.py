class Wallet():
    # флаг на изменение (при любых изменениях ставить его в true)
    change = False

    # флаг на изменение курса
    kurs_change = False

    # флаг на сохранение данных
    save_flag = False

    # данные
    amount = {'rub': 0.0,
              'eur': 0.0,
              'usd': 0.0,
              }

    # инициализация
    def __init__(self, usd, eur, rub):
        self.amount['rub'] = rub
        self.amount['usd'] = usd
        self.amount['eur'] = eur

    # изменения в amount
    def changer(self, usd=None, eur=None, rub=None):
        args = {'usd': usd, 'eur': eur, 'rub': rub}
        for arg in args:
            if args[arg] is not None:
                self.amount[arg] = args[arg]
                # флаг об изменениях в amount
                self.change = True

    def _set_curs(self, data):
        for key in data:
            self.amount[key] = data[key]
        self.change = True

    def is_change(self):
        if self.change or self.kurs_change:
            result = {}

            if self.change is True:
                self.change = False
                result = self.get()

            if self.kurs_change is True:
                self.kurs_change = False
                result = {'kurs': True,
                          'USD-RUB': '{:.2f}'.format(self.amount['USD-RUB']),
                          'EUR-RUB': '{:.2f}'.format(self.amount['EUR-RUB'])}
            return result

    # возврат значений
    def get(self):

        # Сумма в рублях
        summa = self.amount['rub'] + \
                + self.amount['eur'] * self.amount['EUR-RUB'] + \
                + self.amount['usd'] * self.amount['USD-RUB']

        # Сумма в долларах
        summa_usd = self.amount['rub'] * self.amount['RUB-USD'] + \
                    + self.amount['usd'] + self.amount['eur'] * self.amount['EUR-USD']

        # Сумма в евро
        summa_eur = self.amount['rub'] * self.amount['RUB-EUR'] + \
                    + self.amount['eur'] + self.amount['usd'] * self.amount['USD-EUR']

        return {'rub': '{:.2f}'.format(self.amount['rub']),
                'usd': '{:.2f}'.format(self.amount['usd']),
                'eur': '{:.2f}'.format(self.amount['eur']),
                'USD-RUB': '{:.2f}'.format(self.amount['USD-RUB']),
                'EUR-RUB': '{:.2f}'.format(self.amount['EUR-RUB']),
                'USD-EUR': '{:.2f}'.format(self.amount['USD-EUR']),
                'EUR-USD': '{:.2f}'.format(self.amount['EUR-USD']),
                'amount_rub': '{:.2f}'.format(summa),
                'amount_usd': '{:.2f}'.format(summa_usd),
                'amount_eur': '{:.2f}'.format(summa_eur),
                'summa': True,
                'kurs': True}


    def set(self, data):
        save_keys = [key for key in data if key != 'mode']
        result = {}
        clean_keys = {}
        old_clean_keys = {}
        first, second, third = False, False, False

        for key in save_keys:
            clean_keys[key] = data[key]

        # установка значений
        if data['mode'] == 'set':

            if clean_keys.get('usd') is None:
                first = True

            else:
                if clean_keys['usd'] >= 0:
                    first = True

            if clean_keys.get('eur') is None:
                second = True

            else:
                if clean_keys['eur'] >= 0:
                    second = True

            if clean_keys.get('rub') is None:
                third = True

            else:
                if clean_keys['rub'] >= 0:
                    third = True

        # изменение значений
        elif data['mode'] == 'modify':
            old_clean_keys = clean_keys.copy()  # для логов

            if clean_keys.get('usd') is None:
                first = True
            else:
                if float(clean_keys['usd']) + self.amount['usd'] >= 0:
                    clean_keys['usd'] = float(clean_keys['usd']) + self.amount['usd']
                    first = True

            if clean_keys.get('eur') is None:
                second = True
            else:
                if float(clean_keys['eur']) + self.amount['eur'] >= 0:
                    clean_keys['eur'] = float(clean_keys['eur']) + self.amount['eur']
                    second = True
            if clean_keys.get('rub') is None:
                third = True
            else:
                if float(clean_keys['rub']) + self.amount['rub'] >= 0:
                    clean_keys['rub'] = float(clean_keys['rub']) + self.amount['rub']
                    third = True

        if (first and second and third):
            self.changer(usd=clean_keys.get('usd'), eur=clean_keys.get('eur'), rub=clean_keys.get('rub'))
            if data['mode'] == 'set':
                result = {key: clean_keys.get(key) for key in save_keys}
                result.update({'status' : 'request has been completed'})

            elif data['mode'] == 'modify':
                result = {'status': 'request has been completed',
                          'usd': old_clean_keys.get('usd'),
                          'eur': old_clean_keys.get('eur'),
                          'rub': old_clean_keys.get('rub')
                          }
            return result
        else:
            return {'status': 'request hasn"t been completed'}