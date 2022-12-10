"""
Card is a card in a standard deck of 52
"""
class Card():

    """
    Constructer for a card given a value
    @param val: value of the card
    """
    def __init__(self, val) -> None:
        self.value = val
        self.number = self.getNumber()
        self.suite = self.getSuite()

    """
    Get the suite of the card
    @param isSmall: if string of length 2 wanted, defaults to false
    @return: string specifying the suite
    """
    def getSuite(self, isSmall=False):
        suites = ["Clubs", "Spades", "Hearts", "Diamonds"]
        if isSmall:
            suites = ["{}", "/\\", "<3", "<>"]
        return suites[self.value%4]

    """
    Get the Number of the card
    @param isSmall: if string of length 2 wanted, defaults to false
    @return: string specifying the number or class of face card
    """
    def getNumber(self, isSmall=False):
        cards = [
            "Ace", "2", "3", "4", "5", "6", "7", "8", "9",
            "10", "Jack", "Queen", "King"
        ]
        if isSmall:
            cards = [" A", " 2", " 3", " 4", " 5", " 6", " 7", " 8", " 9",
            "10", " J", " Q", " K"]
        return cards[int(self.value / 4)]

    """
    Generalized function to get the value of a card
    @param card: Card type
    @return: retuns the value of the card
    """
    def getValue(card):
        return card.value

    """
    @return: Returns a string specifying the cards number and suite
    """
    def toString(self):
        return self.number + " of " + self.suite

    """
    @param id: player ip address
    @return: returns a string of the cards number and suite, isSmall specified as true
    """
    def prt(self):
        return self.getNumber(True) + self.getSuite(True)

    """
    gets file name under which the cards image is storeed
    @return: string of the cards file name
    """
    def getPath(self):
        return self.getSuite().lower() + "_" + self.getNumber().lower()


class Table():

    """
    Constructs a Table
    @param cards: list of any initial cards, defaults to None
    """
    def __init__(self, cards=None) -> None:
        if cards == None:
            self.flop = None
            self.turn = None
            self.river = None
        else:
            self.flop = cards[0:3]
            self.turn = cards[3]
            self.river = cards[4]

    """
    @return: a string containing the cards of the table
    """
    def toString(self) -> str:
        back = "[{}]"
        line = "-"*32
        rtn = line+ "\n"+ "| "

        # Flop
        if self.flop == None:
            rtn += back + " " + back + " " + back + " | "
        else:
            rtn += self.flop[0].prt() + " " + self.flop[1].prt() + " " + self.flop[2].prt() + " | "
        
        # Turn
        if self.turn == None:
            rtn += back + " | "
        else:
            rtn += self.turn.prt() + " | "
        
        # River
        if self.river == None:
            rtn += back + " |"
        else:
            rtn += self.river.prt() + " |"
        
        # Combine and return
        rtn += "\n"+line
        return rtn
    
    """
    Gets a specified card
    @param num: number corisponding to wich card is wanted
    @return: that card.getPath(), so the path of that card, false if no card
    """
    def getTableCard(self, num):
        card = None
        # Flop
        try:
            if num == "1":
                card = self.flop[0]
            elif num == "2":
                card = self.flop[1] 
            elif num == "3":
                card = self.flop[2] 
        except:
            card = None
        if num == "4":
            # Turn
            card = self.turn
        elif num == "5":
            # River
            card = self.river
        if card == None:
            # Card not exist
            return False
        return card.getPath()


class DiscardPile():

    """
    Constructs a DiscardPile
    """
    def __init__(self) -> None:
        self.cards = []

    """
    Add a card to the discard pile
    @param card: card
    """
    def discard(self, card):
        if card != None:
            self.cards.append(card)
    
    """
    clears the discardPile
    """
    def clear(self):
        self.cards = []

   
class Player():

    """
    Construct a Player
    @param id: player ip address
    @param name: player name
    """
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        self.money = 0
        self.card1 = None
        self.card2 = None
        self.propho = "sources?p=sources/propho/profile-blank.webp"

    """
    Get a string indicating the players name, money, and hand
    @return: string of player infomation
    """
    def toString(self):
        # Name
        rtn = self.name + (16-len(self.name))*" "

        # Money
        mon = str(self.money)

        # Cards
        rtn += " [" + (4-len(mon))*"0" + mon + "] " 
        if self.card1 == None:
            rtn += "---- "
        else: 
            rtn += self.card1.prt()+" "
        if self.card2 == None:
            rtn += "----"
        else: 
            rtn += self.card2.prt()
        return rtn

    def addMoney(self, value):
        try:
            val = int(value)
            self.money += val
        except:
            pass


class GameStats():

    """
    Construct BaseLine game stats
    """
    def __init__(self) -> None:
        self.starterMoney = 100
        self.smallBlind = 2
        self.bigBlind = 4
        self.maxRaise = 4
        self.style = "online"

    def setStat(self, stat, value):
        if stat.lower() in ["sb", "smallblind"]:
            try:
                val = int(value)
                if val >= 0 and val < self.starterMoney / 5 and val <= self.bigBlind: 
                    self.smallBlind = val
            except:
                pass
        if stat.lower() in ["bb", "lb", "bigblind", 'largeblind']:
            try:
                val = int(value)
                if val >= 0 and val < self.starterMoney /5 and val >= self.smallBlind:
                    self.bigBlind = val
            except:
                pass
        if stat.lower() in ["maxraise","raise"]:
            try:
                val = int(value)
                if val >= 1:
                    self.maxRaise = val
            except:
                pass
        if stat.lower() in ["startingmoney","startermoney","beginingmoney", "basemoney"]:
            try:
                val = int(value)
                if val >= 10:
                    self.starterMoney = val
            except:
                pass
        if stat.lower in ["style"]:
            if value in ["online","local"]:
                self.style = value


class TableLayout():

    """
    Constructs a tableLayout
    @param players: list of all players with the given player removed
    """
    def __init__(self, players) -> None:
        self.players = players
        self.layoutList = self.generateTableLayout()
        
    """
    Generates this players tableLayout
    @return: list of what each player spot should look like, 
            given player name and profile photo
    """
    def generateTableLayout(self):
        # Base Line status
        baseProPho = "sources?p=sources/propho/profile-blank.webp"
        spot1 = ["invalid", baseProPho]
        spot2 = ["invalid", baseProPho]
        spot3 = ["invalid", baseProPho]
        spot4 = ["invalid", baseProPho]
        spot5 = ["invalid", baseProPho]
        spot6 = ["invalid", baseProPho]
        spot7 = ["invalid", baseProPho]

        # Hanlde n number of players
        if len(self.players) == 1:
            spot4 = self.getName(0)
        elif len(self.players) == 2:
            spot3 = self.getName(0)
            spot5 = self.getName(1)
        elif len(self.players) == 3:
            spot2 = self.getName(0)
            spot4 = self.getName(1)
            spot6 = self.getName(2)
        elif len(self.players) == 4:
            spot2 = self.getName(0)
            spot3 = self.getName(1)
            spot5 = self.getName(2)
            spot6 = self.getName(3)
        elif len(self.players) == 5:
            spot2 = self.getName(0)
            spot3 = self.getName(1)
            spot4 = self.getName(2)
            spot5 = self.getName(3)
            spot6 = self.getName(4)
        elif len(self.players) == 6:
            spot1 = self.getName(0)
            spot2 = self.getName(1)
            spot3 = self.getName(2)
            spot5 = self.getName(3)
            spot6 = self.getName(4)
            spot7 = self.getName(5)
        elif len(self.players) == 7:
            spot1 = self.getName(0)
            spot2 = self.getName(1)
            spot3 = self.getName(2)
            spot4 = self.getName(3)
            spot5 = self.getName(4)
            spot6 = self.getName(5)
            spot7 = self.getName(6)
        
        # return list of player spots
        return [spot1,spot2,spot3,spot4,spot5,spot6,spot7]
        
    """
    puts the name and profile photo together of a given player
    @param num: player number
    @return: list of player name and player profile photo
    """
    def getName(self, num):
        rtn = [self.players[num].name , self.players[num].propho]
        return rtn