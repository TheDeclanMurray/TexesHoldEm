from comparater import CompHands
from attributes import Table

def playAHandTerminal(self):
    self.isPlaying = True
    # Shuffle
    self.shuffle(6)
    # Deal Cards
    for player in self.players:
        player.card1 = self.Deck.pop(0)
    for player in self.players:
        player.card2 = self.Deck.pop(0)
        print(player.toString())
    # Bet Pre Flop
    self.playersBet(True)
    # Flop
    self.DiscardPile.discard(self.Deck.pop(0))
    self.table.flop = [self.Deck.pop(0), self.Deck.pop(0), self.Deck.pop(0)]
    print(self.table.toString(),"[$",self.pot,"]")
    # Bet the Flop
    self.playersBet()
    # Turn
    self.DiscardPile.discard(self.Deck.pop(0))
    self.table.turn = self.Deck.pop(0)
    print(self.table.toString(),"[$",self.pot,"]")
    # Bet the Turn
    self.playersBet()
    # River
    self.DiscardPile.discard(self.Deck.pop(0))
    self.table.river = self.Deck.pop(0)
    self.DiscardPile.cards = self.DiscardPile.cards + self.Deck
    self.Deck = []
    print(self.table.toString(),"[$",self.pot,"]")
    # Bet the River
    self.playersBet()
    # Evaluate
    compHands = CompHands(self.table)
    for i in range(0, len(self.players)):
        if not self.isFlopped[i]:
            compHands.addPlayer(self.players[i])
    # for player in self.players:
    #     compHands.addPlayer(player)
        # print(player.name + (16 - len(player.name))*" "  + best)
    winners = compHands.whoWins()
    print("Winner: -->>>> ",winners)
    for player in self.players:
        if player.name in winners:
            player.money = player.money + int(self.pot/len(winners))
        print(player.name,player.money)
    self.pot = 0

    # Discard each hand
    for player in self.players:
        self.DiscardPile.discard(player.card1)
        self.DiscardPile.discard(player.card2)
        player.card1 = None
        player.card2 = None

    tableCards = self.table.flop + [self.table.turn, self.table.river]
    self.table = Table()
    self.DiscardPile.cards = self.DiscardPile.cards + tableCards
    # Deck = Discard
    self.Deck = self.DiscardPile.cards
    self.DiscardPile.cards = []


    self.dealer = (self.dealer + 1) % len(self.players)
    self.isPlaying = False


def playersBetTerminal(self, isPreFlop=False):
    print("                                      Players Bet")
    # print("Dealer:",self.dealer,self.players[self.dealer].name)
    playerBets = len(self.players)*[0]
    matchValue = 0
    lastRaise = (self.dealer + 1) % len(self.players)
    if isPreFlop:
        # set up floppedValue
        for i in range(len(self.players)):
            self.isFlopped[i] = False
        # small Blind
        smallBlindSpot = (self.dealer+1)%len(self.players)
        smallBlind = self.players[smallBlindSpot]
        if smallBlind.money >= self.gameStats.smallBlind:
            smallBlind.money = smallBlind.money - self.gameStats.smallBlind
            playerBets[smallBlindSpot] = self.gameStats.smallBlind
            self.pot = self.pot + self.gameStats.smallBlind
            print(smallBlind.name, "SBs", self.gameStats.smallBlind)
        else:
            print(smallBlind.name, "is Broke lol")
            self.isFlopped[smallBlindSpot] = True
        # big Blind
        bigBlindSpot = (self.dealer+2)%len(self.players)
        bigBlind = self.players[bigBlindSpot]
        if bigBlind.money >= self.gameStats.bigBlind:
            bigBlind.money = bigBlind.money - self.gameStats.bigBlind
            playerBets[bigBlindSpot] = self.gameStats.bigBlind
            self.pot = self.pot + self.gameStats.bigBlind
            lastRaise = (bigBlindSpot+1)%len(self.players)
            matchValue = self.gameStats.bigBlind
            print(bigBlind.name, "BBs", self.gameStats.bigBlind)
        else:
            print(smallBlind.name, "is Broke lol")
            self.isFlopped[bigBlindSpot] = True
        # everyone Else
        for i in range(len(self.players)-2):
            playerNum = (self.dealer + 3 + i) % len(self.players)
            player = self.players[playerNum]
            bet = self.askPlayerForBet(player, matchValue)
            if bet == False:
                self.isFlopped[playerNum] = True
                print(player.name, "folded --", bet)
            else:
                if bet > matchValue: # meaning they raised
                    print("                 Raise")
                    matchValue = bet
                    lastRaise = playerNum
                # move the money
                player.money = player.money - bet
                self.pot = self.pot + bet
                playerBets[playerNum] = bet



    # if not pre-flop
    else:
        # starting from the small blind, players who are still in bet untill pot matched or 1 person left
        for i in range(len(self.players)):
            playerNum = (i+self.dealer+1)%len(self.players)
            if not self.isFlopped[playerNum]:
                player = self.players[playerNum]
                bet = self.askPlayerForBet(player, matchValue)
                if bet == False:
                    self.isFlopped[playerNum] = True
                    print(player.name, "folded --", bet)
                else:
                    if bet > matchValue: # meaning player raised
                        matchValue = bet
                        lastRaise = playerNum
                    # move the money
                    player.money = player.money - bet
                    self.pot = self.pot + bet
                    playerBets[playerNum] = bet
            
    
    # if the pot is not whole make it whole
    currSpot = (self.dealer + 1) % len(self.players)
    while currSpot != lastRaise:
        if not self.isFlopped[currSpot]:
            player = self.players[currSpot]
            bet = self.askPlayerForBet(player, matchValue - playerBets[currSpot]) 
            if isinstance(bet, bool) and bet == False:
                self.isFlopped[currSpot] = True
                print(player.name, "folded --", bet)
            else:
                if bet > matchValue-playerBets[currSpot]: # meaning player raised 
                    matchValue = bet+playerBets[currSpot] 
                    lastRaise = currSpot 
                # move the money 
                player.money = player.money - bet 
                self.pot = self.pot + bet 
                playerBets[currSpot] = playerBets[currSpot] + bet 


        currSpot = (currSpot + 1) % len(self.players)


            
# Does not move the money only deturmins the value
# handles flops for self.isFlopped[] - not anymore
# matchValue is the amount of money left to match
def askPlayerForBet(self, player, matchValue): 
    isValidBet = False
    while not isValidBet:
        inp = input( str(matchValue) + " to "+player.name+" bet: ")
        try:
            bet = int(inp)
            isValidBet = (
                bet <= player.money and # if player has the money
                bet >= matchValue and # if it matches
                bet <= matchValue + self.gameStats.maxRaise # if it does not exeed the raise l
            )
            if isValidBet:
                self.addToChat(player.name +" bets $"+inp)
                return bet
        except:
            if inp.lower() == "fold":
                self.addToChat(player.name+" folds")
                return False
            if inp.lower() in ["call",""]:
                self.addToChat(player.name+" matches $"+matchValue)
                return matchValue
            if inp.lower() == "raise":
                self.addToChat(player.name+" raises $"+str(matchValue + self.gameStats.maxRaise))
                return matchValue + self.gameStats.maxRaise
            print("Not a Valid Input")

