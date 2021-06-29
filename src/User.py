class User:
    def __init__(self, name: str, gender: str, age: int, weight: int, height: int, allergies: list, likes: list, dislikes: list):
        self.name = name
        self.gender = gender
        self.age = age
        self.weight = weight
        self.height = height
        self.allergies = allergies
        self.likes = likes
        self.dislikes = dislikes
        self.caloriePerMeal = round(self.getDailyCalorieIntake() / 4)   #4 porque eh numero refeicoes dia

    def getAge(self):
        return self.age

    def getWeight(self):
        return self.weight

    def getGender(self):
        return self.gender

    def getHeight(self):
        return self.height

    def getAllergies(self):
        return self.allergies

    def getCaloriePerMeal(self):
        return self.caloriePerMeal

    def getDailyCalorieIntake(self):
        if self.gender == "M":
            return (66.5 + (13.8*self.weight) + (5*self.height) - 6.8*self.age) * 1.375
        else:
            return (655.1 + (9.5 * self.weight) + (1.8 * self.height) - 4.7 * self.age) * 1.375

    def getLikes(self):
        return self.likes

    def getDislikes(self):
        return self.dislikes

    def __repr__(self):
        return "{}, {}, {}, {}, {}, {}, {}, {}\n".format(self.name, self.gender, self.age, self.weight,  self.height, self.allergies, self.likes, self.dislikes)
