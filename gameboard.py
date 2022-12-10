from random import randint
from attributes import Card, Table, DiscardPile, Player, GameStats, TableLayout
from comparater import CompHands
import os  

class PokerTable():

    """
    @param gameStats: gameStats object, defaluts to None
    """
    def __init__(self, gameStats=None) -> None:
        # Player Atributes
        self.players = []
        self.isFolded = []
        self.Bets = len(self.players)*[0]
        self.dealer = 0
        self.whoseTurn = 0
        self.lastRaise = 1
        self.tableLayouts = self.genTableLayouts()

        # Game Atributes
        self.gameStatus = "deal"            # "deal" "bet" "reveal"
        self.firstTimeRound = True
        self.currStep = 0
        self.table = Table()
        self.Deck = self.generateCards()
        self.DiscardPile = DiscardPile()
        if gameStats == None:
            gameStats = GameStats()
        self.gameStats = gameStats 
        self.pot = 0
        self.matchValue = 0
        self.chat = ["Game Started"]
        self.compHands = None

    """
    Shuffle the deck in a humanistic, yet still random way
    @param num: number of shuffles, defaults to 6
    """
    def shuffle(self, num=6):
        # Shuffle num times
        for i in range(0,num):

            # split the deck in half
            frontHalf = self.Deck[0:26]
            backHalf = self.Deck[26:52]
            self.Deck = []

            # Shuffle once
            isFront = True
            while len(frontHalf)>0 or len(backHalf)>0:
                if isFront:
                    # Card from Front Deck
                    if len(frontHalf)==0:
                        # Front deck done
                        self.Deck = self.Deck+backHalf
                        backHalf = []
                    else:
                        # deturmin front or back
                        self.Deck.append(frontHalf.pop(0))
                        rand = randint(1,10)
                        if rand < 8:
                            isFront = False
                else:
                    # Card from Back Deck
                    if len(backHalf)==0:
                        # Back deck done
                        self.Deck = self.Deck+frontHalf
                        frontHalf = []
                    else:
                        # deturmin front or back
                        self.Deck.append(backHalf.pop(0))
                        rand = randint(1,10)
                        if rand < 8:
                            isFront = True
        
        # Split the Deck
        split = randint(6,48)
        front = self.Deck[:split]
        back = self.Deck[split:]
        self.Deck = back+front

    """
    Completes an action based on the current stage of the game
    @param inp: input, [userIp,bet]
    """
    def playAHand(self, inp):
        # Shuffle and Deal Cards
        if self.currStep == 0:
            # Set up variables
            self.gameStatus = "bet"
            self.whoseTurn = self.dealer
            
            # Shuffle
            self.shuffle(6)
            
            # Deal Cards
            for player in self.players:
                player.card1 = self.Deck.pop(0)
            for player in self.players:
                player.card2 = self.Deck.pop(0)
            
            # set up floppedValue, matchValue and lastRaise
            for i in range(len(self.players)):
                self.isFolded[i] = False
                self.Bets[i] = 0
            self.matchValue = 0
            self.lastRaise = (self.dealer + 1) % len(self.players)
            
            # Small Blind
            smallBlindSpot = (self.dealer+1)%len(self.players)
            smallBlind = self.players[smallBlindSpot]
            if smallBlind.money >= self.gameStats.smallBlind:
                # Has the money, Small Blind Extraction
                smallBlind.money = smallBlind.money - self.gameStats.smallBlind
                self.Bets[smallBlindSpot] = self.gameStats.smallBlind
                self.pot = self.pot + self.gameStats.smallBlind
                self.matchValue = self.gameStats.smallBlind
                self.lastRaise = smallBlindSpot
                self.addToChat("SB",smallBlind.name+" bets $"+str(self.gameStats.smallBlind))
            else:
                # Does not have the money, auto Folds
                self.addToChat("Fold",smallBlind.name+" Has No Money")
                self.isFolded[smallBlindSpot] = True
                if self.checkFolded():
                    return
            
            # Big Blind 
            bigBlindSpot = (self.dealer+2)%len(self.players)
            bigBlind = self.players[bigBlindSpot]
            if bigBlind.money >= self.gameStats.bigBlind:
                # Has the money, Big Blind Extraction
                bigBlind.money = bigBlind.money - self.gameStats.bigBlind
                self.Bets[bigBlindSpot] = self.gameStats.bigBlind
                self.pot = self.pot + self.gameStats.bigBlind
                self.lastRaise = (bigBlindSpot+1)%len(self.players)
                self.matchValue = self.gameStats.bigBlind
                self.addToChat("LB", bigBlind.name+" bets $"+str(self.gameStats.bigBlind))
            else:
                # Does not have the money, auto Folds
                self.addToChat("Fold", bigBlind.name+" Has No Money")
                self.isFolded[bigBlindSpot] = True
                if self.checkFolded():
                    return

            # Finish 
            self.currStep += 1
            self.whoseTurn = (bigBlindSpot+1)%len(self.players)
            return 

        # Bet Pre-Flop
        if self.currStep == 1:
            if inp[0] == self.players[self.whoseTurn].id:
                # if its the right person they bet
                lastBet = self.playerBets(inp)
                if self.checkFolded():
                    return 
                if lastBet:
                    # Flop
                    self.DiscardPile.discard(self.Deck.pop(0))
                    self.table.flop = [self.Deck.pop(0), self.Deck.pop(0), self.Deck.pop(0)]
                    self.addToChat("Table", "Flop Revealed")

                    # Finish
                    self.currStep += 1
                    self.whoseTurn = (self.dealer+1)%len(self.players)
                    self.lastRaise = self.whoseTurn
                    self.firstTimeRound = True
                    self.matchValue = 0
                    for i in range(0,len(self.players)):
                        self.Bets[i] = 0
            return 

        # Bet Flop
        if self.currStep == 2:
            if inp[0] == self.players[self.whoseTurn].id:
                # if its the right person they bet
                lastBet = self.playerBets(inp)
                if self.checkFolded():
                    return 
                if lastBet:
                    # Turn
                    self.DiscardPile.discard(self.Deck.pop(0))
                    self.table.turn = self.Deck.pop(0)
                    self.addToChat("Table", "Turn Revealed")

                    # Finish
                    self.currStep += 1
                    self.whoseTurn = (self.dealer+1)%len(self.players)
                    self.lastRaise = self.whoseTurn
                    self.firstTimeRound = True
                    self.matchValue = 0
                    for i in range(0,len(self.players)):
                        self.Bets[i] = 0
            return 
        # Bet Turn
        if self.currStep == 3:
            if inp[0] == self.players[self.whoseTurn].id:
                # if its the right person they bet
                lastBet = self.playerBets(inp)
                if self.checkFolded():
                    return 
                if lastBet:
                    # River
                    self.DiscardPile.discard(self.Deck.pop(0))
                    self.table.river = self.Deck.pop(0)
                    self.DiscardPile.cards = self.DiscardPile.cards + self.Deck
                    self.Deck = []
                    self.addToChat("Table", "River Revealed")

                    # Finish
                    self.currStep += 1
                    self.whoseTurn = (self.dealer+1)%len(self.players)
                    self.lastRaise = self.whoseTurn
                    self.firstTimeRound = True
                    self.matchValue = 0
                    for i in range(0,len(self.players)):
                        self.Bets[i] = 0
            return
        # Bet River
        if self.currStep == 4:
            if inp[0] == self.players[self.whoseTurn].id:
                # if its the right person they bet
                lastBet = self.playerBets(inp)
                if self.checkFolded():
                    return 
                if lastBet:
                    # Finish
                    self.currStep += 1
                    self.gameStatus = "reveal"
                    self.lastRaise = self.whoseTurn
                    self.matchValue = 0
                    for i in range(0,len(self.players)):
                        self.Bets[i] = 0
                    self.compHands = CompHands(self.table)
            return 
        # Handle Reveal
        if self.currStep == 5:
            # Get Player and PlayerSpot
            player = self.getPlayer(inp[0])
            playerSpot = self.players.index(player)

            # dicounting any Folded or Previously submitted players
            if self.isFolded[playerSpot]:
                return
            if player in self.compHands.players:
                return
            
            # Calculate best Hand
            besthand = self.compHands.addPlayer(player)
            self.addToChat("Hand", player.name + ": " + besthand[3:])
            
            # is all hands are revealed
            for i in range(0,len(self.players)):
                if not self.isFolded[i]:
                    if not self.compHands.containsPlayer(self.players[i].name):
                        # not all unfolded players in Comp
                        return
            
        # all hands revealed
            # handle winners money
            winners = self.compHands.whoWins()
            chatReading = "$"+str(self.pot)+" Goes To"
            for player in self.players:
                if player.name in winners:
                    player.money = player.money + int(self.pot/len(winners))
                    chatReading += " "+player.name
            self.pot = 0
            self.addToChat("Win", chatReading)

            # Discard each hand
            for player in self.players:
                self.DiscardPile.discard(player.card1)
                self.DiscardPile.discard(player.card2)
                player.card1 = None
                player.card2 = None

            # Discard the Table
            tableCards = self.table.flop + [self.table.turn, self.table.river]
            self.table = Table()
            self.DiscardPile.cards = self.DiscardPile.cards + tableCards
            
            # Deck = Discard
            self.Deck = self.DiscardPile.cards
            self.DiscardPile.cards = []

            # Finish
            self.currStep = 0
            self.dealer = (self.dealer + 1) % len(self.players)
            self.whoseTurn = self.dealer
            self.gameStatus = "deal"
            self.lastRaise = self.whoseTurn
            self.firstTimeRound = True
            self.matchValue = 0
            for i in range(0,len(self.players)):
                self.Bets[i] = 0

    """
    handles player bet
    @param inp: input, [userIp,bet]
    @return: true if last bet for current round, false if otherwise
    """
    def playerBets(self, inp):
        # Get player and playerSpot
        player = self.getPlayer(inp[0])
        playerSpot = self.players.index(player)

        # Check if betting should be over (I think redundent)
        if playerSpot == self.lastRaise:
            if self.firstTimeRound:
                self.firstTimeRound = False
            else:
                return True
        
        # Hanlde player bet
        try:
            # get bet
            bet = int(inp[1])
            isValidBet = (
                bet <= player.money and # if player has the money
                bet >= self.matchValue-self.Bets[playerSpot] and # if it matches
                bet <= self.matchValue + self.gameStats.maxRaise # if it does not exeed the raise l
            )
            if isValidBet:
                if inp[1] == "0":
                    # Check
                    self.addToChat("Bet", player.name +" Checks")
                else:
                    # Bet
                    self.addToChat("Bet", player.name +" bets $"+inp[1])
                
                # on Raise
                if bet > self.matchValue-self.Bets[playerSpot]: # meaning player raised 
                    self.matchValue = bet+self.Bets[playerSpot] 
                    self.lastRaise = playerSpot
                
                # move the money
                player.money = player.money - bet
                self.pot = self.pot + bet
                self.Bets[playerSpot] = self.Bets[playerSpot] +  bet
                
                # handle player turns
                return self.turnEnded()
        except:
            if inp[1].lower() == "fold":
                # Handle Fold
                self.addToChat("Fold", player.name)
                self.isFolded[playerSpot] = True
                return self.turnEnded()
            elif inp[1].lower() == "call":
                # Handle "Call" (unreachable)
                self.addToChat("Bet", player.name+" matches $"+self.matchValue)
                # move the money
                bet = self.matchValue - self.Bets[playerSpot]
                player.money = player.money - bet
                self.pot = self.pot + bet
                self.Bets[playerSpot] = self.matchValue
                return self.turnEnded()

        # Handle if not valid bet input
        print(player.name,"Not a Valid Bet")
        return False                
            
    """
    checks if current betting stage is over and deturmin whoseTurn it is next
    @return: true if last bet for current round, false if otherwise
    """
    def turnEnded(self):
        # incriment whoseTurn
        self.whoseTurn = (self.whoseTurn+1)%len(self.players)
        while self.isFolded[self.whoseTurn]:
            # Check if betting over
            if (self.whoseTurn == self.lastRaise):
                return True
            # iderate through folded players
            self.whoseTurn = (self.whoseTurn+1)%len(self.players)
        # check if betting over
        if (self.whoseTurn == self.lastRaise):
            return True
        return False
        
    """
    checks if all but one player has folded, and handles that situation
    @return: true if one player left unfoled, false if otherwise
    """
    def checkFolded(self):
        # Calc the number of unfolded players
        numUnfolded = 0
        for foldStatus in self.isFolded:
            if not foldStatus:
                numUnfolded += 1
        if numUnfolded > 1:
            # enough players
            return False
        if numUnfolded < 1:
            # too few players
            print("big Issues here!!!")
            return False
        
        # get winner
        chatReading = "$"+str(self.pot)+" Goes To"
        for playerSpot in range(0,len(self.players)):
            if self.isFolded[playerSpot] == False:
                winner = self.players[playerSpot]

        # handle winner and money
        for player in self.players:
            if player.id == winner.id:
                player.money = player.money + int(self.pot)
                chatReading += " "+player.name
        self.pot = 0
        self.addToChat("Win", chatReading)

        # Discard each hand
        for player in self.players:
            self.DiscardPile.discard(player.card1)
            self.DiscardPile.discard(player.card2)
            player.card1 = None
            player.card2 = None

        # Discard the Table
        if self.table.flop != None:
            for c in self.table.flop:
                self.DiscardPile.discard(c)
        self.DiscardPile.discard(self.table.turn)
        self.DiscardPile.discard(self.table.river)
        self.table = Table()
        
        # Deck = Discard
        self.Deck = self.DiscardPile.cards
        self.DiscardPile.cards = []

        # Finish
        self.currStep = 0
        self.dealer = (self.dealer + 1) % len(self.players)
        self.whoseTurn = self.dealer
        self.gameStatus = "deal"
        self.lastRaise = self.whoseTurn
        self.firstTimeRound = True
        self.matchValue = 0
        for i in range(0,len(self.players)):
            self.Bets[i] = 0
        return True

    """
    @return: an array of all 52 cards
    """
    def generateCards(self):
        rtn = []
        for num in range(0, 52):
            # create a list of all 52 cards
            crd = Card(num)
            rtn.append(crd)
        return rtn
        
    """
    Adds a new player to the game
    @param id: id of player
    @param name: name of player
    @param propho: profile photo path
    @return: new player if player added, false if not a valid name
    """
    def addPlayer(self, id, name, propho):
        # check to make sure player name not taken
        for p in self.players:
            if p.name == name:
                return False
        
        # create new Player
        newPlayer = Player(id, name)
        newPlayer.money = self.gameStats.starterMoney

        # hanlde profile photo
        if propho != None and propho != "":
            # if not given a path
            propho = os.path.abspath("./sources/propho/"+propho)
            basePath = "/Users/declanmurray/Desktop/CompSci/Python Projects/TexesHoldEm/sources/propho/"
            if propho.startswith(basePath) and os.path.exists(propho):
                # if path exists and is valid
                propho = "sources?p=" + propho[58:]
                newPlayer.propho = propho

        # Update game atributes 
        self.players.append(newPlayer)
        self.isFolded.append(True)
        self.Bets.append(0)
        self.genTableLayouts()
        self.addToChat("New", newPlayer.name + " joined")
        return newPlayer

    """
    Remove a player from the game
    @param id: player ip address
    @return: true if player removed, false if id not matched
    """
    def removePlayer(self, id):
        # Find the player
        i = 0
        for p in self.players:
            if p.id == id:
                # Remove the player
                self.players.pop(i)
                self.isFolded.pop(i)
                self.Bets.pop(i)
                self.genTableLayouts()
                if len(self.players) != 0:
                    self.dealer = self.dealer % len(self.players)
                    self.whoseTurn = self.whoseTurn % len(self.players)

                # discard players cards
                self.DiscardPile.discard(p.card1)
                self.DiscardPile.discard(p.card2)
                self.addToChat("Left", p.name+" left the game")
                self.checkFolded()
                return True
            i += 1
        return False

    """
    Get player given an ip address
    @param id: player ip address
    @return: player if player found, false if id not matched
    """
    def getPlayer(self, id):
        # Look for player id
        for player in self.players:
            if player.id == id:
                return player
        return False

    """
    Get table card
    @param num: card number
    @return: the num table card
    """
    def getTableCard(self, num):
        return self.table.getTableCard(num)

    """
    Adds a message to Chat
    @param type: type of chat message
    @param tag: message
    """
    def addToChat(self, type, tag):
        if type == "Table":
            # no type tag for "Table"
            line = tag
        else:
            line = "["+type+"]"
            spacer = (7-len(type))*"."
            line = line + spacer + tag

        # Add to Chat, remove exess elements
        self.chat.insert(0,line)
        if len(self.chat) > 22:
            self.chat.pop(22)

    """
    Checks if player is the dealer via ip address
    @param id: player ip address
    @return: true if player is the dealer, false if not
    """
    def isDealer(self, ip):
        return (self.players[self.dealer].id == ip)

    """
    Generate Table Layouts for each player
    @return: the new tableLayouts
    """
    def genTableLayouts(self):
        newTableLayouts = []

        # for each player
        for i in range(0, len(self.players)):
            players = self.players.copy()
            players.pop(i)
            if len(self.players) == 1:
                players = []

            # compute and add table layout
            newLayout = TableLayout(players)
            layoutlist = newLayout.layoutList
            newTableLayouts.append(layoutlist)
        self.tableLayouts = newTableLayouts
        return newTableLayouts

    """
    Gets a table layout given player ip address
    @param id: player ip address
    @return: table layout of specified player, false if id not matched
    """
    def getTableLayout(self, id):
        # search through players
        for playerSpot in range(0, len(self.players)):
            if self.players[playerSpot].id == id:
                return self.tableLayouts[playerSpot]
        return False