import datetime
import random
import copy
import numpy as np
from statistics import mean
from math import ceil
import CentralUnit
from Ingredient import Ingredient

class FridgePantry:
    def __init__(self, id: int, recipes: list, ing_flags: dict, ing_quantsPerMeal: dict, ing_types: dict, cu: CentralUnit, canAsk = True):
        self.id = id
        self.canAsk = canAsk
        self.cu = cu
        self.users = []
        self.allergies = set()
        self.date = datetime.date(2021, 1, 1)
        self.recipes = recipes      #todas as refeicoes globais
        self.ing_flags = ing_flags  #info sobre ings e regras de partilha, dict {string: flag}
        self.ing_quantsPerMeal = ing_quantsPerMeal  #do tipo { string: quantidade per meal }
        self.ing_types = ing_types  #info sobre ings e a sua unicade, dict {string: unidade}
        self.ingredients = []
        self.ingredients_w = {}     #dicionario com nome alimento (str): peso que representa importancia/uso (float)
        self.sugestions = []
        self.meals = []             #refeicoes ja executadas pelos users
        self.mealsFeedback = []
        self.shoppingDic = {}       #{ ingredient(str) : quantity to buy (media por ingrediente x users x 2 ) }
        self.garbage = []
        self.garbageWasteValue = 0  #metrica para avaliacao do lixo
        self.meanCaloriePerMeal = 0
        self.donators = {}          #guarda doadores para cada receita, do tipo {receita: {ingrediente: id} }
        self.likes = set()
        self.dislikes = set()
        self.automaticFeedbackCenter = 2.5      #valor central do intervalo de feedbacks
        self.automaticFeedbackIncr = 1        #valor adicionado/removido ao center consoante gosto/desgosto de ingr
        self.automaticFeedbackRange = 0.25       #valor adicionado e removido a center para ter intervalo
        self.automaticChoiceDistribution = {1: [1], 2: [0.75, 0.25], 3: [0.5, 0.3, 0.2], 4: [0.4, 0.3, 0.2, 0.1], 5:
                                            [0.3, 0.3, 0.2, 0.1, 0.1]}
        self.wed = 50/100
        self.wci = 0/100
        self.wst = 50/100
        self.weightUpdate = 0.7
        self.buy_meals = 100
        self.likeToBuy = 2.6
        self.quantityToBuy = 2
        self.initialWeight = 2.5

    def setWeights(self, wed, wci, wst):
        self.wed = wed
        self.wci = wci
        self.wst = wst


    def getId(self):
        return self.id

    def getUsers(self):
        return self.users

    def getIngredients(self):
        return self.ingredients

    def getMeanCaloriesPerMeal(self):
        return self.meanCaloriePerMeal

    def getGarbageWasteValue(self):
        return self.garbageWasteValue

    def getWeights(self):
        return self.ingredients_w

    def getIngredientsNames(self):
        res = [ing.getName() for ing in self.ingredients]
        return res

    def getIngredientByName(self, ingName):
        ingredient = None
        for ing in self.ingredients:
            if ing.getName() == ingName:
                ingredient = ing
        return ingredient

    def getIngQuantPerMeal(self, ingName):
        """retorna quantidade per meal do ingredient (str) fornecido"""
        return self.ing_quantsPerMeal[ingName]

    def addUser(self, user):
        self.users.append(user)
        self.allergies.update(user.getAllergies())    #adicionar alergias de user a alergias geral
        self.likes.update(user.getLikes())
        #print("likes: ",self.likes)
        self.dislikes.update(user.getDislikes())
        self.updateCaloriePerMeal()
        self.removeRecipesWithAllergies(user.getAllergies())

    def collectGarbage(self):
        for ing in self.ingredients:
            if ing.getExpirationDate()[0][0] < self.date:       #ingrediente tem produto com ED
                ingWasted = copy.copy(ing)
                ingWasted.setExpiracionData(ingWasted.getExpirationDate()[0])
                self.garbage.append(ingWasted)
                self.garbageWasteValue += self.calcIngredientValue(ingWasted)
                self.removeIngredient(ing.getName(), quantity=ing.getExpirationDate()[0][1])

    def calcIngredientValue(self, ing):
        if self.ing_types[ing.getName()] == 'g' or self.ing_types[ing.getName()] == 'mL':
            ingWeight = 1
        else:
            ingWeight = 45
        return ing.getQuantity() + ingWeight

    def refreshShoppingList(self):
        ingsStoredNames = self.getIngredientsNames()
        for ingName in self.ingredients_w:
            if self.ingredients_w[ingName] > self.likeToBuy:   #ingrediente com classificacao acima de 3.5
                if ingName in ingsStoredNames:      #ingrediente ja existe no FP
                    ing = self.getIngredientByName(ingName)
                    if ing.getQuantity() < self.ing_quantsPerMeal[ingName] * len(self.users) * 2:  #nao ha quantidade para fazer duas refeicoes
                        self.shoppingDic[ingName] = (self.ing_quantsPerMeal[ingName] * len(self.users) * self.quantityToBuy) - ing.getQuantity()
                else:                               #ingrediente nao existe e eh add a lista de compras
                    self.shoppingDic[ingName] = self.ing_quantsPerMeal[ingName] * len(self.users) * self.quantityToBuy
        #para remover qb's que tem valor a 0
        self.shoppingDic = {key: val for key, val in self.shoppingDic.items() if val != 0}

    def addIngredient(self, newIng):
        ingsInFridge = self.getIngredients()
        ingExists = False
        eDExists = False
        for ing in ingsInFridge:
            if newIng.getName() == ing.getName():
                ing.updateQuantity(newIng.getQuantity())
                for eD in ing.getExpirationDate():
                    if newIng.getExpirationDate()[0][0] == eD[0]:    #caso em que ja existe o produto com essa dV
                        eD[1] += newIng.getQuantity()
                        eDExists = True
                        break
                if not eDExists:
                    ing.getExpirationDate().append(newIng.getExpirationDate()[0])  #posicao 0 para tirar lista dentro de lista

                ing.sortExpirationDate()  #ordenacao das dV para ficarem dV's menores nas primeiras posicoes
                ingExists = True
                break

        if not ingExists:
            self.ingredients.append(newIng)
            self.ingredients_w[newIng.getName()] = self.initialWeight        #ingrediente comeca com weight 0

        #caso o ingrediente esteja na lista de compras
        if newIng.getName() in self.shoppingDic:
            if newIng.getQuantity() >= self.shoppingDic[newIng.getName()]:   #quantidade adicionada eh pelo menos a da lista de compras
                del self.shoppingDic[newIng.getName()]
            else:
                self.shoppingDic[newIng.getName()] -= newIng.getQuantity()

    def updateCaloriePerMeal(self):
        aux = []
        for u in self.users:
            aux.append(u.getCaloriePerMeal())
        self.meanCaloriePerMeal = round(sum(aux) / len(aux))

    def removeIngredient(self, ingredientName, quantity):
        nIngredients = len(self.ingredients)
        for i in range(nIngredients):
            if self.ingredients[i].getName() == ingredientName:
                expDs = self.ingredients[i].getExpirationDate()
                while quantity > 0:
                    if quantity > expDs[0][1]:      #ha mais para remover do que na nesta eD
                        self.ingredients[i].updateQuantity(-expDs[0][1])
                        quantity -= expDs[0][1]     #removeu tudo o que havia nesta eD
                        expDs.pop(0)
                    else:                           #removeu a quantidade nesta eD e nao sobra nada para remover
                        expDs[0][1] -= quantity
                        self.ingredients[i].updateQuantity(-quantity)
                        quantity = 0
                        if expDs[0][1] == 0:    #eD ficou com zero de quantidade
                            expDs.pop(0)
                if len(self.ingredients[i].getExpirationDate()) == 0:   #caso a lista de eV's tenha ficado vazia
                    self.getIngredients().pop(i)
                break

    def removeRecipesWithAllergies(self, userAllergies):
        aux = []
        for r in self.recipes:
            removeFlag = False
            for allergie in userAllergies:
                for ingName in r.getIngredientsNames():
                    if allergie in ingName and allergie != '':      #ex: "Tomate" in "Polpa de Tomate"
                        removeFlag = True
                        break
                else: continue                   #para sair de 2 ciclos
                break
            if not removeFlag:
                aux.append(r)
        self.recipes = aux

    def getRankingED(self, p_recipes):
        """Recebe uma lista de refeicoes possiveis e retorna uma lista ordenada por ED com a posicao
            das receitas da linha inicial"""
        aux = {}
        ingsNamesStored = [ing.getName() for ing in self.ingredients]   #lista com os nomes dos ingredientes
        for r in p_recipes:                    #para todas as receitas possiveis
            ingExpirationList = []
            for ingName in r.getIngredientsNames():       #para cada ingrediente em cada receita
                for i in range(len(ingsNamesStored)):
                    if ingName == ingsNamesStored[i]:       #se eu tiver esse ingrediente
                        ingExpirationList.append(abs(self.ingredients[i].getExpirationDate()[0][0] - self.date).days)  #meto numa lista auxiliar a diferença
            aux[r.getName()] = sum(ingExpirationList) / len(ingExpirationList)
        sorted_recipes = sorted(aux.items(), key=lambda x: x[1], reverse=False)
        return sorted_recipes

    def getRankingCI(self, p_recipes):
        """Recebe uma lista de refeicoes possiveis e retorna uma lista ordenada por CI recomendado
            com a posicao das receitas da linha inicial"""
        aux = {}
        for r in p_recipes:
            aux[r.getName()] = abs(self.meanCaloriePerMeal - self.getHypotheticWMeanCI(7, r))
        sorted_recipes = sorted(aux.items(), key=lambda x: x[1], reverse=False)
        return sorted_recipes

    def getRankingST(self, p_recipes):
        """Recebe uma lista de refeicoes possiveis e retorna uma lista ordenada por Self Taste recomendado
            com a posicao das receitas da linha inicial"""
        aux = {}
        for r in p_recipes:
            aux[r.getName()] = self.getValueOfRecipe(r)
        sorted_recipes = sorted(aux.items(), key=lambda x: x[1], reverse=True)
        return sorted_recipes

    def getValueOfRecipe(self, recipe):
        value = 0
        for ing in recipe.getIngredientsNames():
            try:
                value += self.ingredients_w[ing]
            except KeyError:                    #ingrediente nunca foi adionado ao FP
                self.ingredients_w[ing] = self.initialWeight     #o peso comeca a 0 mas depois leva feedback
        value /= len(recipe.getIngredientsNames())
        return value

    def getSuggestion(self, n):
        p_recipes = self.getPossibleRecipes()
        #print("\npossiveis: {}\n".format(p_recipes))
        #print("ingredientes: {}\n".format(self.ingredients))
        #print("possible", p_recipes)
        globalRanks = {}
        for rec in p_recipes:   #ciclo a iniciar
            globalRanks[rec.getName()] = []
        r_ed = self.getRankingED(p_recipes)  #lista ordenada por prioridade ExpirationDate, posicoes representam posicoes nas p_recipes
        r_ci = self.getRankingCI(p_recipes)  #lista ordenada por prioridade CaloricIntake
        r_st = self.getRankingST(p_recipes)  #lista ordenada por prioridade SelfTaste
        #print("red", r_ed, "\n")
        #print("rci", r_ci, "\n")
        #print("rst", r_st, "\n")
        nRecipes = len(p_recipes)
        for i in range(nRecipes):
            globalRanks[r_ed[i][0]].append(i * self.wed)            #para ter em conta os pesos
            globalRanks[r_ci[i][0]].append(i * self.wci)
            globalRanks[r_st[i][0]].append(i * self.wst)

        #print("Global ranks:", globalRanks)
        sortedRanks = sorted(globalRanks.items(), key=lambda x: sum(x[1]))
        #print("Recipes sorted:", sortedRanks)
        self.sugestions=[]
        if len(sortedRanks) < n: n = len(sortedRanks)                    ##para o caso de receitas possiveis < n
        for j in range(n):
            suggestionName = sortedRanks[j][0]
            for rec in p_recipes:
                if suggestionName == rec.getName():
                    self.sugestions.append(rec)
        if len(self.sugestions) > 0: self.addRecipeNotTried(p_recipes)
        return self.sugestions

    def addRecipeNotTried(self, possible):
        recipes = list(set(possible) - set(self.meals) - set(self.sugestions))
        try:
            random_recipe = random.choice(recipes)
            self.sugestions[-1] = random_recipe
        except IndexError:
            pass

    def getQuantityOfIngredientInRecipe(self, recipe, ingredientName):
        nIngredients = len(recipe.getIngredientsNames())
        for i in range(nIngredients):
            if recipe.getIngredientsNames()[i] == ingredientName:
                return recipe.getQuantity()[i]

    def buyShoppingList(self):
        shoppingList = self.shoppingDic.copy()
        for name, quantity in shoppingList.items():
            ingredient = Ingredient(name=name, quantity=quantity, expirationDate=self.date + datetime.timedelta(days=5))
            self.addIngredient(ingredient)

    def finishedMeal(self, feedback):
        if len(self.meals) % 2 == 0:  # incrementar dia de 2 em 2 refeicoes
            self.date += datetime.timedelta(days=1)
            self.collectGarbage()  # coletar todos os ingredientes fora de validade
        if len(self.meals) % self.buy_meals == 0:
            self.buyShoppingList()
        if feedback == "a":
            #automatic feedback
            feedback = self.automaticFeedback()
            print("Automatic Feedback is {}".format(feedback))
        self.meals[-1].updateFeedback(feedback)
        self.mealsFeedback.append(feedback)
        for ing in self.meals[-1].getIngredientsNames():     #update dos pesos dos ingredientes
            self.ingredients_w[ing] = round(self.ingredients_w[ing] * (1-self.weightUpdate) + feedback * self.weightUpdate, 2)

        #print("PESOS: \n", self.ingredients_w)
        if len(self.meals) > 0:             #cold start, 5 receitas para perceber gosto dos users
            self.refreshShoppingList()
        return feedback

    def automaticFeedback(self):
        lastMeal = self.meals[-1]
        lastMealIngredients = lastMeal.getIngredientsNames()
        for ingName in lastMealIngredients:
            if ingName in self.likes: #and self.automaticFeedbackCenter <= 4.5:
                #print("Eu gosto do ingrediente {}".format(ingName))
                #print("Automatic Range antes era {} e agora é {}".format(self.automaticFeedbackCenter,self.automaticFeedbackCenter+0.5))
                self.automaticFeedbackCenter += self.automaticFeedbackIncr
            elif ingName in self.dislikes: #and self. automaticFeedbackCenter >= 0.5:
                #print("Eu nao gosto do ingrediente {}".format(ingName))
                #print("Automatic Range antes era {} e agora é {}".format(self.automaticFeedbackCenter,self.automaticFeedbackCenter - 0.5))
                self.automaticFeedbackCenter -= self.automaticFeedbackIncr

        newAutomatic = self.automaticFeedbackCenter
        self.automaticFeedbackCenter = 2.5
        feedback = round(random.uniform(newAutomatic-self.automaticFeedbackRange, newAutomatic+self.automaticFeedbackRange), 1)
        return np.clip(feedback, 0, 5)  #garante que valor esa entre 0 e 5

    def selectRecipe(self, n):
        if n == "a":
            n = self.automaticChoice(len(self.sugestions))
            print("The automatic choice is {}".format(n))
        recipe = self.sugestions[n-1]
        self.sugestions = []  # eh dado reset por ja foi selecionada
        if recipe.getDoable() == 1:  #se eu tiver todos os ingredientes desta receita
            self.removeQuantitiesFromRecipe(recipe.getIngredientsNames(), recipe)
        else:
            missingIngredients, possessedIngredients, semiPossessedIngredients = self.getMissingIngredients(recipe.getIngredientsNames(), recipe)
            self.removeQuantitiesFromRecipe(possessedIngredients, recipe)
            self.removeFullQuantitiesFromFP(semiPossessedIngredients)
            to_remove = {}                                         #vai construir dicionario para pedir remoção
            for ing in missingIngredients:
                to_remove[self.donators[recipe][ing]] = []
            for ing in missingIngredients:                         #vai ser do tipo {id : [ingrediente (str), quantity]}
                to_remove[self.donators[recipe][ing]].append([ing, missingIngredients[ing]])
            self.cu.askIngredients(to_remove, self.getId())
        self.donators = {}
        self.meals.append(recipe)

        return str(recipe), recipe.getDescription()

    def automaticChoice(self, n):
        return np.random.choice(np.arange(1, n+1), p=self.automaticChoiceDistribution[n])

    def getMissingIngredients(self, recipeIngredients, recipe):
        """Retorna quais os missing ingredients no formato pedido pela AskIngredients do cu e quais os ingredientes que
        este frigorifico possui no formato da funcao removeQuantitiesFromRecipe"""
        missingIngredients = {}
        possessedIngredients = []
        semiPossessedIngredients = []
        my_ings = self.getIngredientsNames()
        for i in recipeIngredients:
            temp = self.getQuantityOfIngredientInRecipe(recipe, i)       #TEMP USADO PARA IGNORAR QVB'S QU VAO TER VALOR A 0
            if i not in my_ings and temp != 0:                 #se eu nao tiver esse ingrediente
                missingIngredients[i] = temp*len(self.users)
            else:
                for ingredient in self.ingredients:
                    if ingredient.getName() == i and ingredient.getQuantity() >= \
                            self.getQuantityOfIngredientInRecipe(recipe, i)*len(self.users):    #se eu tiver tudo desse ingrediente
                        possessedIngredients.append(i)
                    elif ingredient.getName() == i and ingredient.getQuantity() < self.getQuantityOfIngredientInRecipe(recipe, i)*len(self.users):  #se eu tiver uma beca desse ingrediente
                        missingIngredients[i] = self.getQuantityOfIngredientInRecipe(recipe, i)*len(self.users) - \
                                                ingredient.getQuantity()
                        semiPossessedIngredients.append(i)

        return missingIngredients, possessedIngredients, semiPossessedIngredients

    def removeFullQuantitiesFromFP(self, semiPossessedIngredients):
        for i in semiPossessedIngredients:
            for j in self.ingredients:
                if i == j.getName():
                    self.removeIngredient(i, j.getQuantity())

    def removeQuantitiesFromRecipe(self, recipeIngredients, recipe):
        """Remove todos os ingredientes do frigorifico"""
        for ingName in recipeIngredients:
            for ing in self.ingredients:
                if ing.getName() == ingName:
                    self.removeIngredient(ingName, self.getQuantityOfIngredientInRecipe(recipe, ingName)*len(self.users))

    def getWMeanCI(self, n, alpha=0.5):
        """recebe numero de dias, e retorna media pesada calorica nesses ultimos dias.
        usa smoothing factor alpha"""
        try:
            res = self.meals[-n:][0].getCaloricValue()
            for m in self.meals[-n+1:]:
                res = res*(1-alpha) + m.getCaloricValue()*alpha
        except IndexError:
            res = 0
        return res

    def getHypotheticWMeanCI(self, n, recipe, alpha=0.5):
        """recebe numero de dias, e retorna media pesada calorica nesses ultimos dias.
        usa smoothing factor alpha"""
        self.meals.append(recipe)
        res = self.meals[-n:][0].getCaloricValue()
        for m in self.meals[-n+1:]:
            res = res*(1-alpha) + m.getCaloricValue()*alpha
        self.meals.pop()
        return res

    def getPossibleRecipes(self):
        p_recipes = []
        for r in self.recipes:
            r_ingredients = r.getIngredientsNames()
            qbs = r.getIngQB()
            my_ingredients = list(map( lambda x: x.getName(), self.ingredients))
            dont_have = [x for x in r_ingredients if x not in my_ingredients]       #ingredientes da receita que eu nao tenho
            if not self.canAsk and len(dont_have) > 0: break                             #se não puder pedir, e existem ings que nao tenho, passo para proxima
            flags = [self.ing_flags[ing] == 0 for ing in dont_have]                 #boolean se ing que nao tenho se pode pedir
            #flags = [True]
            request, _, semiP = self.getMissingIngredients(r.getIngredientsNames(), r)
            donators = self.cu.checkIngredients(self.id, request)
            if len(set(dont_have+semiP) - set(qbs)) == 0:                           #se todos os que nao tenho forem qb's
                p_recipes.append(r)
                r.setDoable(1)
            elif False not in flags and len(donators) > 0:             #se houver False, há ingrediente que nao tenho que nao posso ped
                self.donators[r] = donators
                p_recipes.append(r)                         #confirma tambem se há donators para o caso de ser preciso
                r.setDoable(0)
        #print("possible recipes with canAsk = ", canAsk)
        #print("with the ings: ", self.ingredients)
        #print("Recipes:", p_recipes)
        return p_recipes

    def getIngWithDV(self, ingrediente: str, quantity):
        for ing in self.ingredients:
            if ing.getName() == ingrediente and ing.getQuantity() >= quantity:
                return self.daysToEndDV(ing.getExpirationDate()[0][0])
        return False

    def daysToEndDV(self, expirationDate: datetime.date):
        days = (expirationDate - self.date).days
        return days

    def getMeanFeedback(self):
        return mean(self.mealsFeedback) if len(self.mealsFeedback) > 0 else 0

    def printShoppingList(self):
        print(self.shoppingDic)

    def __repr__(self):
        id = "FridgePantry:\n" + str(self.getId()) + "\n"
        users = "Users:\n"
        for u in self.users:
            users += str(u)
        ingredients = "Ingredients:\n"
        for ing in self.ingredients:
            ingredients += str(ing)[:-1]    #-1 para retirar um \n que fica no fim
        allergies = "\nAllergies:\n{}\n".format(self.allergies)
        garbage = "Garbage:\n"
        for g in self.garbage:
            garbage += str(g)[:-1]
        garbage += "\nGarbage waste value: {}\n".format(self.garbageWasteValue)
        meanFeeback = "Mean Feedback: {}\n".format(self.getMeanFeedback())
        normalAvgCalories = "Healthy calories per meal: {}\t\t".format(self.getMeanCaloriesPerMeal())
        avgCaloriesConsumed = "Average Calories Consumed: {}\t".format(self.getWMeanCI(10))
        deviation = "Deviation from healthiest calories number: {}\n".format(self.getWMeanCI(10) - self.getMeanCaloriesPerMeal())
        weights = "Ingredient weights: {}\n".format(self.ingredients_w)
        return id + users + ingredients + garbage + meanFeeback + normalAvgCalories + avgCaloriesConsumed + deviation + weights