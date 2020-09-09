class Wallet():
    DataAboutCashLocal = {}
    DataAboutCourseLocal = {}

    def __init__(self, CashInPocket):
        assert type(CashInPocket) is dict, 'NOT DICT'
        self.DataAboutCashLocal = CashInPocket

    def CheckChangeCashInPocket(self, DataAboutCash):
        isChange = False
        assert type(DataAboutCash) is dict, 'NOT DICT'
        if DataAboutCash != self.DataAboutCashLocal:
            for key, value in DataAboutCash.items():
                    self.DataAboutCashLocal[key] = DataAboutCash[key]
            isChange = True
        if isChange is True:
            return True
        else:
            return False

    def CheckChangeCourseValute(self, DataAboutCourse):
        isChange = False
        assert type(DataAboutCourse) is dict, 'NOT DICT'
        if DataAboutCourse != self.DataAboutCourseLocal:
            for key, value in DataAboutCourse.items():
                self.DataAboutCourseLocal[key] = DataAboutCourse[key]
            isChange = True
        if isChange is True:
            return True
        else:
            return False






