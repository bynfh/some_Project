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
            if Valute not in self.CashInWallet:
                Messege = 'This valute unsupported:{valute}'.format(valute=Valute)
                raise AssertionError(Messege)
            elif ValuteValues[Valute] != self.CashInWallet[Valute]:
                self.CashInWallet[Valute] = Values
                self.isChangeCash = True


    def ModifyCashInWallet(self,ValuteValues):
        assert type(ValuteValues) is dict, 'NOT DICT'
        for Valute, Values in ValuteValues.items():
            if Valute not in self.CashInWallet:
                Messege = 'This valute unsupported:{valute}'.format(valute=Valute)
                raise AssertionError(Messege)
            else:
                self.CashInWallet[Valute] += Values
                self.isChangeCash = True

    def SetRate(self, Rate):
        assert type(Rate) is dict, 'NOT DICT'
        if Rate != self.Rate:
            for valute, values in Rate.items():
                self.Rate[valute] = values
            self.isChangeCourse = True

    def GetAmountInAnyValute(self,valute):
        assert type(valute) is str, 'NOT STR'
        amount = 0
        for valute_x, cash_x in self.CashInWallet.items():
            NeedRate = valute_x.upper() + '-' + valute.upper()
            if NeedRate not in self.Rate:
                raise AssertionError(['This valute unsupported', valute])
            amount += int((cash_x * self.Rate[NeedRate]))
        return amount

    def GetValuesCashInWallet(self,valute):
        if valute not in self.CashInWallet:
            raise AssertionError(['This valute unsupported', valute])
        else:
            return self.CashInWallet[valute]















