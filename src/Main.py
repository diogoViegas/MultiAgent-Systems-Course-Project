import sys
import json
import datetime
from FridgePantry import FridgePantry
from Ingredient import Ingredient
from Recipe import Recipe
from Parser import Parser
from CentralUnit import CentralUnit
from statistics import mean

recipe_path = 'data/recipes.json'
food_path = "data/food.json"
input_path = "input/tovideo.txt"
################################################
############    GLOBAL VARIABLES    ############
################################################
debug = False
canAsk = True
cu = CentralUnit()

################################################
############    AUXILIAR METHODS    ############
################################################
def getListFromCommas(line):
    res = []
    for i in line.split(","):
        res.append(i)
    return res

def getFPById(idFridge):
    for fp in cu.getFPs():
        if fp.getId() == idFridge:
            return fp

recipes = Parser.readRecipes(recipe_path)
ing_flags, ing_quantsPerMeal, ing_types = Parser.readIngredients(food_path, recipes)

for r in recipes:
    r.updateToUnitaryQuantities()

l = 1
for line in sys.stdin:
    #a = input()
    if line !="\n": print("Comando:\t{}\n".format(line))
    if debug:
        print("#################################################################" + "\n")
        print("line:", l, ", " + line)

    if line.startswith("end"):
        if True:
            all_feeds = []
            all_trash = []
            all_devIC = []
            for fp in cu.getFPs():
                #print(fp)
                m = fp.getMeanFeedback()
                t = fp.getGarbageWasteValue()
                d = abs(fp.getWMeanCI(10) - fp.getMeanCaloriesPerMeal())
                all_feeds.append(m)
                all_trash.append(t/1000)
                all_devIC.append(d)
            #print("Mean Feedback of the system:\t", mean(all_feeds))
            #print("Mean WastValue of the system:\t", mean(all_trash))
            #print("Mean DeviationIC of the system:\t", mean(all_devIC))
            #print("Fedbacks:\t{} ->Mean:\t{}".format(all_feeds,mean(all_feeds)))
            #print("Trahs:\t{} ->Mean\t{}".format(all_trash, mean(all_trash)))
            #print("CI Deviations:\t{} ->Mean:\t{}".format(all_devIC,mean(all_devIC)))
            #print("Exchanges:\t", sorted(cu.getExcahnges().items()))
        break

    elif line.startswith("set weights"):
        s = line.split(" ")
        id = int(s[2])        #id do agente
        fp = getFPById(id)
        wed, wci, wst = s[3:]
        fp.setWeights(float(wed), float(wci), float(wst))


    elif line.startswith("add FridgePantry"):
        s = line.split(" ")
        id = int(s[2])        #id do agente
        fp = FridgePantry(id, recipes, ing_flags, ing_quantsPerMeal, ing_types, cu, canAsk=canAsk)
        cu.addFP(fp)
        if debug:
            print("--Added FP {}--".format(id) + "\n")

    elif line.startswith("add User"):  #add User Carla F 65 200 160 N
        user = Parser.readUser(line)    #retorna objecto user
        cu.getFPs()[-1].addUser(user)    #adiciona user ao ultimo FP

        if debug:
            print("--Added User to FP {}--".format(cu.getFPs()[-1].getId()))
            print(user)

    elif line.startswith("add Ingredient"):
        idFridge, ingredient = Parser.addIngredient(line)
        fp = getFPById(idFridge)
        fp.addIngredient(ingredient)
        if debug:
            print("--Added Ingredient to FP {}--".format(idFridge))
            print(ingredient)

    elif line.startswith("remove Ingredient"):
        s = line.split(" ")
        idFridge = int(s[2])
        ingredientName = s[3]
        quantity = int(s[4])
        fp = getFPById(idFridge)
        fp.removeIngredient(ingredientName, quantity)
        if debug:
            print("--Removed Ingredient from FP {}--".format(idFridge))

    elif line.startswith("show Ingredients"):
        s = line.split(" ")
        idFridge = int(s[2])
        fp = getFPById(idFridge)
        ingrs = fp.getIngredients()
        print("Ingredients in FP {}: {}".format(idFridge, ingrs))

    elif line.startswith("get Suggestion"):
        s = line.split(" ")
        idFridge = int(s[2])
        # TODO: meter aqui a flag para pedir a outros ou nao
        fp = getFPById(idFridge)
        sugs = fp.getSuggestion(5)
        print("\nSuggestions to ",idFridge)
        if len(sugs) == 0: print("None Available")
        else:
            for s in sugs:
                print(s)
        print("")


    elif line.startswith("choose Suggestion"):
        s = line.strip().split(" ")
        idFridge = int(s[2])
        if len(s)==4:
            choice = int(s[3])
        else:
            choice = "a"
        fp = getFPById(idFridge)
        recipe, description = fp.selectRecipe(choice)
        ci = fp.getWMeanCI(5)
        print("Suggestion choosen: ", recipe)
        print("Description: ", description)
        print("")
        #print("current WMeanCI: ", ci)

    elif line.startswith("give Feedback"):
        s = line.strip().split(" ")
        idFridge = int(s[2])
        if len(s)==4:
            feedback = float(s[3])
        else:
            feedback = "a"
        fp = getFPById(idFridge)
        f = fp.finishedMeal(feedback)
        print("Gave feedback: ", f)
        print("")


    elif line.startswith("show ShoppingList"):
        s = line.split(" ")
        idFridge = int(s[2])
        fp = getFPById(idFridge)
        fp.printShoppingList()

    elif line.startswith("get ing_weights"):
        s = line.split(" ")
        idFridge = int(s[2])
        fp = getFPById(idFridge)
        weights = fp.getWeights()
        print("Weights:\n{}\n".format(weights))
    else:
        pass

    l += 1

#sys.stdout.write(agent.recharge()+'\n');