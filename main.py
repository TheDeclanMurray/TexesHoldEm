from gameboard import PokerTable
from flask import Flask, render_template, request, send_file, send_from_directory
import os

if __name__ == "__main__":

    host = None # Not yet Implemented

    # Object the contains and runs the poker game
    pokerTable = PokerTable()
    # Handles client server comunication
    app = Flask(__name__)

    # /home is the home page
    @app.route("/home")
    def welcome():
        return render_template("homepage.html",errorMessage="")

    # /leaveGame removes that ip address and navigates the the home page
    @app.route("/leaveGame")
    def leaveGame():
        user_ip = request.remote_addr 
        pokerTable.removePlayer(user_ip)
        return render_template("homepage.html",errorMessage="Thanks For Playing")

    @app.route("/host")
    def hostGame():
        user_ip = request.remote_addr
        if user_ip != "127.0.0.1":
            return "you are not the Host"
        command = request.args.get("c")
        handleCommand(command)
        
        data={"chat":pokerTable.chat}
        return render_template("hostTerminal.html",data=data)

    def handleCommand(command):
        # try:
            if command == None:
                return
            command = command.lower()
            command = command.split(" ")
            print(command)
            # if command[0] == "help":
            #     help = """help
            #     kick <playerName>
            #     ban <playerName>
            #     giveMoney <playerName> <value>"""
            if command[0] == "kick":
                for p in pokerTable.players:
                    if p.name.lower() == command[1]:
                        pokerTable.removePlayer(p.id)
                        return
                print("player name",command[1],"not in table")
            if command[0] == "ban":
                # TODO: bannable
                print(command[1],"banned")
            if command[0] == "newgame":
                # newTable = PokerTable(pokerTable.gameStats)
                # for p in pokerTable.players:
                #     newTable.addPlayer(p.id,p.name,p.propho)
                pass
            if command[0].startswith("gamestat"):
                pokerTable.gameStats.setStat(command[1],command[2])
                print("GameStat",command[1], "changed to",command[2])
            if command[0] == "givemoney":
                for p in pokerTable.players:
                    if p.name.lower() == command[1]:
                        p.addMoney(command[2])
        # except Exception as e:
        #     print("                               <<<Error>>>\n",e)


    @app.route("/centerpiece")
    def centerPiece():
        # if pokerTable.gameStats.style != "local":
        #     return "not applicable"
        refreshRate = "5000"                             # client refresh rate
        pot = "$"+str(pokerTable.pot)                    # money in the pot
        delt = 0                                         # if hands have been delt
        if pokerTable.table.flop != None:
            delt = 1
        if pokerTable.table.turn != None:
            delt = 2
        if pokerTable.table.river != None:
            delt = 3

        data={"refreshRate":refreshRate,"pot":pot,"delt":delt}
        return render_template("centerPiece.html",data=data)

    # /table is where the game is played
    # url encoded inputs include: 
    #    n : player name
    #    p : platform
    #    b : bet quantity
    #    d : dealed status
    #    r : reveal status
    #    i : profile photo path
    @app.route("/table")
    def joins():
        
        # grab the URL encodeed path
        playerName = request.args.get("n")
        if(playerName == None):
            playerName = "TempName"
        if(playerName == "invalid"):
            return render_template("homepage.html",errorMessage="Invalid Name")
        user_ip = request.remote_addr 
        if(playerName.startswith("God!:")): # Host status
            playerName = playerName[5:]
            host = user_ip
        platform = request.args.get("p")         # "comp" or "phone"
        bet = request.args.get("b")              # "call" "fold" "[num]"
        deal = request.args.get("d")             # "true"
        reveal = request.args.get("r")           # "true"
        propho = request.args.get("i")           # profile photo path
        
        # Check Player In
        newPlayer = True
        player = None
        for p in pokerTable.players:
            if p.id == user_ip:
                playerName = p.name
                newPlayer = False
                player = p
            elif p.name == playerName:
                # name already in use, reject name
                return render_template("homepage.html",errorMessage="Name Already In Use")
        
        print("\n<<<>>>", playerName, user_ip, platform)

        # handle if player is new
        if newPlayer:
            if len(pokerTable.players) < 8: # Max players is 8
                player = pokerTable.addPlayer(user_ip, playerName, propho)
            else:
                return render_template("homepage.html",errorMessage="Game Full")

        # Set up Stats
        refresh = "true"                                 # if the client auto refreshes
        refreshRate = "5000"                             # client refresh rate
        alertMessage = "N/A"                             # alert message, "N/A" is not displayed
        chat = pokerTable.chat                           # list of actions in game
        pot = "$"+str(pokerTable.pot)                    # money in the pot
        matchValue = str(4)                              # current value player must match
        raiseTo = str(8)                                 # maximum raise
        myMoney = "$"+str(player.money)                  # players current money
        dealer = "false"                                 # if player is dealer
        isDelt = "true"                                  # if hands have been delt
        showHand = "true"                                # player hand visibility 
        button = "Deal"                                  # player action button, "Deal" or "Reveal"
        tableLayout = pokerTable.getTableLayout(user_ip) # names and profile photos for other plaeyrs

    # Run the Table
        if pokerTable.gameStatus == "bet":
            print("   GameStatus Bet")
            # Betting Stage
            if user_ip == pokerTable.players[pokerTable.whoseTurn].id:
                # player is currently betting
                if bet == None:
                    # player has not bet yet
                    refresh = "false"
                    alertMessage = "$"+str(pokerTable.matchValue - pokerTable.Bets[pokerTable.whoseTurn])+" Call"
                    matchValue = str(pokerTable.matchValue - pokerTable.Bets[pokerTable.whoseTurn])
                    raiseTo = str(pokerTable.matchValue - pokerTable.Bets[pokerTable.whoseTurn] + pokerTable.gameStats.maxRaise)
                else:
                    # player submitted a bet value
                    pokerTable.playAHand([user_ip, bet])
                    refresh = "true"
                    refreshRate = "1000"
            else:
                # player not betting
                refresh = "true"

        if pokerTable.gameStatus == "deal":
            print("   GameStatus Deal")
            # Deal Stage
            if user_ip == pokerTable.players[pokerTable.dealer].id:
                # player is the dealer
                if deal == None:
                    # player has not delt yet
                    refresh = "false"
                    dealer = "true"
                    isDelt = "false"
                    showHand = "false"
                else:
                    # player has delt
                    pokerTable.playAHand([user_ip, 0])
                    refresh = "true"
                    refreshRate = "1000"
            else:
                # player is not the dealer
                refresh = "true"
                isDelt = "false"
                showHand = "false"
        if pokerTable.gameStatus == "reveal":
            print("   GameStatus Reveal")
            # Reveal Stage
            showHand = "false"
            playerSpot = pokerTable.players.index(player)
            if not pokerTable.isFolded[playerSpot]:
                # If player is unfoled
                if not pokerTable.compHands.containsPlayer(playerName):
                    # if player has not revealed
                    if reveal == None:
                        # prompt reveal
                        button = "Reveal"
                        refreshRate = "2000"
                        showHand = "false"
                    else: 
                        # execute reveal
                        pokerTable.playAHand([user_ip, 0])
                        showHand = "false"
                        refreshRate = "1000"

        # Handle platform, computer or mobile
        if platform == "phone":
            platform = "phoneHand.html"
            chat = chat[:15]
        else:
            platform = "computerHand.html"
        myMoney = "$"+str(player.money) 

        # acumulate all variables into a dictionary
        data = {'refresh':refresh,"alertMessage":alertMessage,"chat":chat,
                "pot":pot,"matchValue":matchValue,"raiseTo":raiseTo,"myMoney":myMoney,
                "dealer":dealer,"isDelt":isDelt,"refreshRate":refreshRate,"button":button,
                "showHand":showHand,"tableLayout":tableLayout}
        return render_template(platform, data=data)
        
    # get image from server
    @app.route('/sources')
    def getImage():
        path = request.args.get("p")
        if path == None:
            return "NOPE"
        fullpath = os.path.abspath(path)
        if not fullpath.startswith("/Users/declanmurray/Desktop/CompSci/Python Projects/TexesHoldEm/sources"):
            # limmit accesability to source file
            return "no Sir"
        return send_file(path, mimetype="image/gif")

    # get table card images from server
    @app.route("/tableCard")
    def getTable():
        # which card
        num = request.args.get("n")
        add = pokerTable.getTableCard(num)
        if add == False:
            add = "back"
        path = "sources/cards/" + add + ".png"
        return send_file(path, mimetype="image/gif")

    # get this players hand card images
    @app.route("/myCards")
    def getHand():
        # which hand card
        num = request.args.get("n")
        user_ip = request.remote_addr
        for p in pokerTable.players:
            if p.id == user_ip:
                card = None
                if num == "1":
                    card = p.card1
                if num == "2":
                    card = p.card2
                if card != None:
                    path = "sources/cards/" + card.getPath() + ".png"
                else:
                    path = "sources/cards/" + "back" + ".png"
                return send_file(path, mimetype="image/gif")
        return "Not Your Card?"

    # get favicon, occasionally called
    @app.route("/favicon.ico")
    def sendFavIcon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                               'sources/favimage.png', mimetype='image/vnd.microsoft.icon')

    # other server calls not yet handled
    # /apple-touch-icon-120x120-precomposed.png
    # /apple-touch-icon-120x120.png
    # /apple-touch-icon-precomposed.png
    # /apple-touch-icon.png

    # run the flask application
    app.run(host="0.0.0.0",port=8080) 

    # terminal inputs from server machine, not yet implemented
    if False:
        #move this to a different thread
        print("running")

        command = [""]
        while not command[0] in ["q","quit","quit()"]:
            command = input("Comand: ").lower()
            command = command.split(" ")
            if command[0] == "help":
                c = """help
                kick <playerName>
                ban <playerName>
                giveMoney <playerName> <value>"""
                print(c)
            if command[0] == "kick":
                pokerTable.removePlayer(command[1])
                print(command[1],"kicked")
            if command[0] == "ban":
                # TODO: bannable
                print(command[1],"banned")
