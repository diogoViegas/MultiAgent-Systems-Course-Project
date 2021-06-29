import FridgePantry

class CentralUnit:
    def __init__(self):
        self.fps = []
        self.exchanges = {}

    def getFPs(self):
        return self.fps

    def getExcahnges(self):
        return self.exchanges

    def addFP(self, fp: FridgePantry):
        self.fps.append(fp)

    def removeFP(self, id: int):        #só para o caso de ser preciso no futuro
        self.fps = [fp for fp in self.fps if fp.getId() != id]

    def checkIngredients(self, requesterId: int, request: dict):
        """recebe o id do fp a fazer request e um dicionario com ingrediente (str): quantidade.
            caso encontre todos os ingredientes, retorna dic do tipo {ingrediente (str): id donator}
            se não encontrar todos, informa requester que não consegui."""

        donators = [fp for fp in self.fps if fp.getId() != requesterId] #todos os fps menos o requester
        final_donators = {}
        for ing in request:
            possible_don = {}                             #possiveis donators para um ingrediente
            for fp in donators:
                dte = fp.getIngWithDV(ing, request[ing])  #retorna days to expire
                if dte:        #dte != False
                    possible_don[fp.getId()] = dte
            if len(possible_don) == 0:
                return {}                                  #caso um ing falhe, retorna lista vazia
            else:
                d = min(possible_don, key=possible_don.get)
                final_donators[ing] = d
        return final_donators

    def askIngredients(self, donations: dict, requesterId: int):
        """recebe dicionario do tipo id : [[ingrediente (str), quantity],...] e informa cada donator que deve remover o ing"""
        donators = [fp for fp in self.fps if fp.getId() in donations.keys()]
        for d in donators:
            id = d.getId()
            key = "".join(sorted([str(id), str(requesterId)]))
            try:
                self.exchanges[key]+=len(donations[id])
            except KeyError:
                self.exchanges[key] = len(donations[id])
            for request in donations[id]:
                d.removeIngredient(request[0], request[1])