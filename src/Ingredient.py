from operator import itemgetter

class Ingredient:
    def __init__(self, name: str, quantity: int, expirationDate):
        self.name = name
        self.quantity = quantity
        self.expirationDate = [[expirationDate, quantity]]
        self.averageQuantityPerMeal = 0  #se for 0 entao eh qb
        self.type = ""

    def getName(self):
        return self.name

    def getQuantity(self):
        return self.quantity

    def getExpirationDate(self):
        return self.expirationDate

    def getQuantityPerMeal(self):
        return self.averageQuantityPerMeal

    def setExpiracionData(self, eD):
        self.expirationDate = eD

    def sortExpirationDate(self):
        self.expirationDate = sorted(self.expirationDate, key=itemgetter(0))

    def updateQuantity(self, diff):
        self.quantity += diff

    def setQuantityPerMeal(self, averageQuantityPerMeal):
        self.averageQuantityPerMeal = averageQuantityPerMeal

    def __repr__(self):
        repr = "{}, {}, {}\n".format(self.name, self.quantity, self.expirationDate)
        return repr