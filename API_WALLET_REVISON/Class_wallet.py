class Wallet():
    CashInWallet = {}
    Rate = {}
    isChangeCash = False
    isChangeCourse = False

    def __init__(self, CashInPocket):
        assert type(CashInPocket) is dict, 'NOT DICT'
        self.CashInWallet = CashInPocket
        self.isChangeCash = True

    def CheckChangeCash(self):
        if self.isChangeCash is True:
            self.isChangeCash = False
            return True
        else:
            return False

    def CheckChangeRate(self):
        if self.isChangeCourse is True:
            self.isChangeCourse = False
            return True
        elif self.Rate == {}:
            return None
        else:
            return False

    def SetCashInWallet(self,ValuteValues):
        assert type(ValuteValues) is dict, 'NOT DICT'
        for Valute, Values in ValuteValues.items():
            if ValuteValues[Valute] != self.CashInWallet[Valute]:
                self.CashInWallet[Valute] = Values
                self.isChangeCash = True


    def ModifyCashInWallet(self,ValuteValues):
        assert type(ValuteValues) is dict, 'NOT DICT'
        for Valute, Values in ValuteValues.items():
            self.CashInWallet[Valute] += Values
            self.isChangeCash = True

    def SetRate(self, Rate):
        assert type(Rate) is dict, 'NOT DICT'
        if Rate != self.Rate:
            for valute, values in Rate.items():
                self.Rate[valute] = values
            self.isChangeCourse = True

    def GetAmountInAnyValute(self,valute):
        amount = 0
        try:
            for valute_x, cash_x in self.CashInWallet.items():
                amount += int((cash_x * self.Rate[valute_x.upper() + '-' + valute.upper()]))
            return amount
        except KeyError:
            raise KeyError("this key is not in dict:{key}".format(key=valute))

    def GetValuesCashInWallet(self,valute):
        try:
            return self.CashInWallet[valute]
        except KeyError:
            raise KeyError("this key is not in dict:{key}".format(key=valute))












