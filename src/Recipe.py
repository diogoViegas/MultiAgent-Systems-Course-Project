from math import ceil

class Recipe:
    def __init__(self, name: str, ingredients, quantity, caloricValue: int, nPeople: int, description: str):
        self.name = name
        self.ingredients = ingredients
        self.quantity = quantity
        self.caloricValue = caloricValue
        self.nPeople = nPeople
        self.feedback = 0.0
        self.description = description
        self.doable = 0                  #1 -> consigo fazer sem ajuda de terceiros

    def getName(self):
        return self.name

    def getIngredientsNames(self):
        return self.ingredients

    def getIngQB(self):
        ings = []
        for i in range(len(self.ingredients)):
            if self.quantity[i] == 0: ings.append(self.ingredients[i])
        return ings

    def getQuantity(self):
        return self.quantity

    def getCaloricValue(self):
        return self.caloricValue

    def getNPeople(self):
        return self.nPeople

    def getDescription(self):
        return self.description

    def getRequest(self):
        request = {}
        for i in range(len(self.ingredients)):
            request[self.ingredients[i]] = self.quantity[i]
        return request

    def setQuantities(self, newQuantities):
        self.quantity = newQuantities

    def updateFeedback(self, newFeeback):
        self.feeback = newFeeback

    def updateToUnitaryQuantities(self):
        newQuantities = []
        for i in self.quantity:
            if isinstance(i, int):
                newQuantities.append(ceil(i/self.nPeople))
            else:
                if i[-1:] == "g":
                    oldQuantity = i[0:-1]
                    newQuantity = int(ceil(int(oldQuantity) / self.nPeople))
                    newQuantities.append(newQuantity)
                elif i[-1:] == "L":
                    oldQuantity = i[0:-2]
                    newQuantity = int(ceil(int(oldQuantity) / self.nPeople))
                    newQuantities.append(newQuantity)
                else:
                    newQuantities.append(0)

        self.setQuantities(newQuantities)

    def getQuantityByIngredientName(self, ingredientName):
        for i in range(len(self.ingredients)):
            if self.ingredients[i] == ingredientName:
                return self.quantity[i]
        return 0

    def setDoable(self, value):
        self.doable = value

    def getDoable(self):
        return self.doable

    def __repr__(self):
        return self.name + " | Calories: " + str(self.caloricValue) + " | Ingredientes: " + str(self.ingredients) \
               + " | Quant: " + str(self.quantity)













