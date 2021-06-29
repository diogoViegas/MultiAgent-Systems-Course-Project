import json
import datetime
from Recipe import Recipe
from User import User
from Ingredient import Ingredient

class Parser:

    @staticmethod
    def readRecipes(path):
        recipes = []
        with open(path) as f:
            data = json.load(f)
            for i in data:
                recipes.append(Recipe(i["Nome"], i["Ingredientes"], i["Quantidades"], i["TeorCalorico"], i["Pessoas"],
                                       i["Descricao"]))
        return recipes

    @staticmethod
    def readIngredients(path, recipes):
        with open(path) as f:
            data = json.load(f)
            keys = data["Nome"]
            values = data["Flag"]
            quantPerMeal = []
            types = []
            for newIng in keys:
                # valor medio de um ingrediente nas receitas
                sumQuantitiesList = []  # tem de ser uma lista e nao um contador porque uma quantity pode ser uma string
                for r in recipes:
                    sumQuantitiesList.append(r.getQuantityByIngredientName(newIng))
                sumQuantitiesWithNo0sList = list(filter((0).__ne__, sumQuantitiesList))
                sumQuantities = 0
                type = ""
                for i in range(len(sumQuantitiesWithNo0sList)):
                    if isinstance(sumQuantitiesWithNo0sList[i], int):
                        sumQuantities += sumQuantitiesWithNo0sList[i]
                        type = "u"
                    elif isinstance(sumQuantitiesWithNo0sList[i], str) and sumQuantitiesWithNo0sList[i][-1:] == "g":
                        sumQuantities += int(sumQuantitiesWithNo0sList[i][0:-1])
                        type = "g"
                    elif isinstance(sumQuantitiesWithNo0sList[i], str) and sumQuantitiesWithNo0sList[i][-1:] == "L":
                        sumQuantities += int(sumQuantitiesWithNo0sList[i][0:-2])
                        type = "mL"
                    else:
                        type = "qb"
                        sumQuantities += 0
                types.append(type)
                quantPerMeal.append(round(sumQuantities / len(sumQuantitiesWithNo0sList)))
            ing_types = dict(zip(keys, types))
            ing_flags = dict(zip(keys, values))
            ing_quantsPerMeal = dict(zip(keys, quantPerMeal))
        return ing_flags, ing_quantsPerMeal, ing_types

    @staticmethod
    def readUser(line):
        u, allerg = line.split("[", 1)
        s = u.split(" ")
        allergies, rest = allerg.split("]", 1)
        newAllergies = allergies.split(",")
        likes, dislikes = rest.split("]", 1)
        newLikes = likes[2:].split(",")
        newDislikes = dislikes[2:-2].split(",")
        user = User(name=s[2], gender=s[3], age=int(s[4]), weight=int(s[5]), height=int(s[6]), allergies=newAllergies, likes=newLikes, dislikes = newDislikes)
        return user

    @staticmethod
    def addIngredient(line):
        #TODO: bug que mete folha de louro com flag 1000, apagar flags
        s = line.strip('\n').split(" ")
        s = list(filter(None, s))
        idFridge = int(s[2])
        #date = s[5].split("/")  # partir string da data
        date = s[-1].split("/")
        name = ' '.join(s[3:-2])
        quantity = s[-2]
        expirationDate = datetime.date(int(date[2]), int(date[1]), int(date[0]))  # tem que ser year/month/day bc america
        ingredient = Ingredient(name=name, quantity=int(quantity), expirationDate=expirationDate)
        return idFridge, ingredient