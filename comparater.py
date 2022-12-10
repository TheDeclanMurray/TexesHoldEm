from attributes import Card

class CompHands():

    """
    Constructs a CompHand
    @param table: table containing 5 cards
    """
    def __init__(self, table) -> None:
        self.tableCards = table.flop + [table.turn,table.river]
        self.players= []

    """
    Add a player to the comparison, computes their best hand
    @param player: of type player
    @return: sting of the best 5 cards this player can make with 
            the table
    """
    def addPlayer(self, player):
        allCards = self.tableCards + [player.card1,player.card2]
        allCards.sort(key=Card.getValue)

        # Test Straight Flush
        suites = [[],[],[],[]] # Clubs, Spades, Hearts, Diamonds
        for c in allCards: # break up into each suite
            suites[c.value%4].append(c)
        for s in suites:
            if len(s) >= 5: # if 5 or more elements in a single suite
                consecutive = self.getConsecutive(s)
                for cons in consecutive:
                    if len(cons) >= 5: # if straight flush
                        bestHand = cons[len(cons)-5:] # grab highest 5
                        bestHand.reverse() # reverse list
                        strReading = "8: " + "!!Straight Flush!! " + bestHand[0].toString()
                        playerInfo = (player.name, strReading, bestHand)
                        self.players.append(playerInfo)
                        return strReading
        
        # Set up Dupes to get quads trips and pairs
        dupes = self.getDupes(allCards)
        quads = []; trips = []; pairs = []
        for d in dupes:
            if len(d) == 4:
                quads = d
            if len(d) == 3:
                trips.append(d)
            if len(d) == 2:
                pairs.append(d)
                
        # Test Quad
        if len(quads) != 0:
            # Fill in kicker and status
            bestHand = self.fillKicker(allCards, quads)
            strReading = "7: " + "Quad "+ bestHand[0].number + "s, " + bestHand[4].number + " Kicker"
            playerInfo = (player.name, strReading, bestHand)
            self.players.append(playerInfo)
            return strReading

        # Test Full House
        if len(trips) > 0 and len(trips)+len(pairs) >= 2:
            # get top trip
            if trips[0][0].number == "Ace":
                topTrip = trips.pop(0)
            else: 
                topTrip = trips.pop(len(trips)-1)
            
            # get highest pair
            topPair = None
            if len(pairs) != 0:
                topPair = pairs[len(pairs)-1]
            
            # convert second trip to pair
            if len(trips) != 0:
                trip2 = trips[0]
                secondTripPair = trip2[:2]
                if topPair == None or secondTripPair[0].value > topPair[0].value:
                    topPair = secondTripPair
            
            # handle Ace Case
            if len(pairs) != 0 and pairs[0][0].number == "Ace":
                topPair = pairs[0]
            
            # return sequence
            bestHand = topTrip + topPair
            strReading = "6: " + "Full House "+ topTrip[0].number + "s over " +topPair[0].number + "s"
            playerInfo = (player.name, strReading, bestHand)
            self.players.append(playerInfo)
            return strReading
            
        # Test Flush
        for suit in suites:
            if len(suit) >= 5:
                # Ace Case
                if suit[0].number == "Ace":
                    k = suit.pop(0)
                    suit.append(k)
                bestHand = suit[len(suit)-5:] # grab highest 5
                bestHand.reverse() # reverse list
                strReading = "5: " + "Flush " + bestHand[0].toString()
                playerInfo = (player.name, strReading, bestHand)
                self.players.append(playerInfo)
                return strReading

        # Test Straight
        consecutive = self.getConsecutive(allCards)
        for cons in consecutive:
            if len(cons) >= 5:
                bestHand = cons[len(cons)-5:] # grab highest 5
                bestHand.reverse()
                strReading = "4: " + "Straight at " + bestHand[0].number
                playerInfo = (player.name, strReading, bestHand)
                self.players.append(playerInfo)
                return strReading
        
        # Test Trips
        if len(trips) > 0:
            highTrip = trips[len(trips)-1]
            # Ace case
            if trips[0][0].number == "Ace":
                highTrip = trips[0]
            bestHand = self.fillKicker(allCards, highTrip)
            strReading = "3: " + "Trip " + bestHand[0].number + "s, "+bestHand[3].number + " " + bestHand[4].number + " kickers"
            playerInfo = (player.name, strReading, bestHand)
            self.players.append(playerInfo)
            return strReading

        # test 2 Pair
        if len(pairs) >= 2:
            topPair = pairs[len(pairs)-1]
            # Ace case
            if pairs[0][0].number == "Ace":
                topPair = pairs[0]
            pairs.remove(topPair)
            secondPair = pairs[len(pairs)-1]
            bestHand = self.fillKicker(allCards, topPair+secondPair)
            strReading = "2: " + "2 Pair: " + bestHand[0].number + "s and "+bestHand[2].number + "s, " + bestHand[4].number + " kicker"
            playerInfo = (player.name, strReading, bestHand)
            self.players.append(playerInfo)
            return strReading
        
        # One Pair
        if len(pairs) == 1:
            bestHand = self.fillKicker(allCards, pairs[0])
            strReading = "1: " + "Pair of " + bestHand[0].number + "s, "+bestHand[2].number + " kicker"
            playerInfo = (player.name, strReading, bestHand)
            self.players.append(playerInfo)
            return strReading

        # High Card
        if allCards[0].number == "Ace": # Ace Case
            k = allCards.pop(0)
            allCards.append(k)
        bestHand = allCards[2:]
        bestHand.reverse()
        strReading = "0: " + bestHand[0].number + " High"
        playerInfo = (player.name, strReading, bestHand)
        self.players.append(playerInfo)
        return strReading

    """
    @param player: [player name, besthand]
    @return: the number of this players best hand,
            refering to the quality of their hand
    """
    def sorter(player):
        return int(player[1][0:1])

    """
    Compute which player(s) win
    @return: list of names of the winners
    """
    def whoWins(self):
        self.players.sort(key=CompHands.sorter)
        self.players.reverse()
        # for p in self.players:
            # print(p[0]," "*(16-len(p[0])),p[1])

        # get the topHands and the topHandVal
        topHands = [self.players[0]]
        topHandVal = int(self.players[0][1][0:1])
        for player in self.players[1:]:
            if topHandVal == int(player[1][0:1]):
                topHands.append(player)
            else:
                break
        # Compare the topHands
        comparisons = [
            CompHands.compareHighCards,       #0
            CompHands.comparePairs,           #1
            CompHands.compare2Pairs,          #2
            CompHands.compareTrips,           #3
            CompHands.compareStraights,       #4
            CompHands.compareFlushs,          #5
            CompHands.compareFullHouses,      #6
            CompHands.compareQuads,           #7
            CompHands.compareStraightFlushs   #8
        ]
        compare = comparisons[topHandVal]
        compare = CompHands.compareHighCards                    # ???
        best = [topHands[0]]
        for player in topHands[1:]:
            comp = compare(best[0][2],player[2])
            if comp == None:
                best.append(player)
            elif not comp:
                best = [player]
        
        # Return Statement
        rtn = []
        for winner in best:
            rtn.append(winner[0])
        return rtn

    """
    Compares two players who both have a straight flush
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compareStraightFlushs(p1, p2):
        return CompHands.compareHighCards(p1,p2)

    """
    Compares two players who both have a 4 of a kind
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compareQuads(p1, p2):
        c1 = int(p1[0].value/4)
        c2 = int(p2[0].value/4)
        if c1 == c2:
            return CompHands.compareHighCards(p1[4:],p2[4:])
        if c1.number == "Ace":
            return True
        if c2.number == "Ace":
            return False
        return c1 > c2

    """
    Compares two players who both have a full house
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compareFullHouses(p1, p2):
        return CompHands.compareHighCards(p1,p2)

    """
    Compares two players who both have a flush
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compareFlushs(p1, p2):
        if p1[4].number == "Ace":
            k = p1.pop(4)
            p1 = [k]+p1
        if p2[4].number == "Ace":
            k = p2.pop(4)
            p2 = [k]+p2
        return CompHands.compareHighCards(p1,p2)

    """
    Compares two players who both have a straights
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compareStraights(p1, p2):
        return CompHands.compareHighCards(p1,p2)

    """
    Compares two players who both have a 3 of a kind
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compareTrips(p1, p2):
        c1 = int(p1[0].value/4)
        c2 = int(p2[0].value/4)
        if c1 == c2:
            return CompHands.compareHighCards(p1[3:],p2[3:])
        if c1.number == "Ace":
            return True
        if c2.number == "Ace":
            return False
        return c1 > c2

    """
    Compares two players who both have two pair
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compare2Pairs(p1, p2):
        c1 = int(p1[0].value/4)
        c2 = int(p2[0].value/4)
        if c1 == c2:
            return CompHands.compare2Pairs(p1[2:],p2[2:])
        if c1.number == "Ace":
            return True
        if c2.number == "Ace":
            return False
        return c1 > c2

    """
    Compares two players who both have a pair
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def comparePairs(p1, p2):
        c1 = int(p1[0].value/4)
        c2 = int(p2[0].value/4)
        if c1 == c2:
            return CompHands.compareHighCards(p1[2:],p2[2:])
        if c1.number == "Ace":
            return True
        if c2.number == "Ace":
            return False
        return c1 > c2

    """
    Compares two players who both have a high card best
    @param p1: player 1
    @param p2: player 2
    @return: True if p1 wins, False if p2 wins, None if its a tie
    """
    def compareHighCards(p1, p2):
        if len(p1) != len(p2):
            print("- - - - Big Error - - - -")
            return None
        for i in range(len(p1)):
            c1 = p1[i]
            c2 = p2[i]
            if int(c1.value/4) < int(c2.value/4):
                if c1.number == "Ace":
                    return True
                return False
            if int(c1.value/4) > int(c2.value/4):
                if c2.number == "Ace":
                    return False
                return True
            # if same, move to next card

    """
    Fill in a players kicker cards
    @param allCards: list of all cards player has access to 
    @param besthand: the best hand kickers excluded
    @return: best hand with kickers
    """            
    def fillKicker(self, allCards, bestHand):
        # Ace Case
        if allCards[0].number == "Ace":
            k = allCards.pop(0)
            allCards.append(k)
        # idderate through all cards from top to bottom
        allCards.reverse()
        rtn = bestHand
        for card in allCards:
            if len(rtn)==5:
                break
            if not (card in bestHand):
                rtn.append(card)
        return rtn

    """
    Remove duplicate cards with the same numebr or face
    @param lst: list of cards
    @return: list with duplicates removed
    """
    def removeDups(self, lst):
        rtn = [lst[0]]
        for e in lst[1:]:
            if int(e.value/4) != int( rtn[len(rtn)-1].value /4):
                rtn.append(e)
        return rtn

    """
    Creates a list of lists of duplicate cards with the same number
    @param list: list of cards
    @return: list of list of cards
    """
    def getDupes(self, lst):
        rtn = []
        curr = [lst[0]]
        for e in lst[1:]:
            if int(e.value/4) == int(curr[len(curr)-1].value/4):
                curr.append(e)
            else:
                rtn.append(curr)
                curr = [e]
        rtn.append(curr)
        return rtn

    """
    Creates a list of lists of consecutive cards
    @param lst: list of cards
    @return: list of list of cards
    """
    def getConsecutive(self, lst):
        lst = self.removeDups(lst)
        # Ace Case
        if int(lst[0].value/4) == 0:
            lst.append(lst[0])
        rtn = []
        currCons = [lst[0]]
        for e in lst[1:]:
            if int(e.value/4) == 1 + int(currCons[len(currCons)-1].value/4):
                currCons.append(e)
            elif e.number == "Ace" and currCons[len(currCons)-1].number == "King":
                currCons.append(e)
            else:
                rtn.append(currCons)
                currCons = [e]
        rtn.append(currCons)
        return rtn

    """
    @param cards: list of cards
    @return: string of cards
    """
    def printCards(self, cards):
        pt=""
        for c in cards:
            pt += c.prt() + " "
        return pt

    """
    @param name: player name
    @return: True if player name in players, false if otherwise
    """
    def containsPlayer(self, name):
        for player in self.players:
            if player[0] == name:
                return True
        return False