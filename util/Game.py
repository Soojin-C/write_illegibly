import random

def newGame(firstPlayer, maxTime = 60, maxRounds = 3): #Creates a new game
    output = {}
    output['players'] = set() #request.sid
    output['correctPlayers'] = set() #Set of players who have correctly guessed the word
    output['order'] = [] #Player order
    output['currDrawer'] = 0 #Index for order
    output['wordPool'] = set() #Word pool
    output['offeredWords'] = ['','',''] #Ask player to choose: apple, pear, banana
    output['currWord'] = '' #apple
    output['wordDisplay'] = '' #__p__
    output['points'] = {} #Dictionary request.sid : score
    output['maxTime'] = maxTime
    output['timerTime'] = maxTime #Current timer
    output['maxRounds'] = maxRounds
    output['round'] = 1
    output['currLines'] = []
    return output

def addUser(game,user): #Adds user to a game
    game['players'].add(user)
    insertPos = int(random.random() * len(game['order']))
    if insertPos <= game['currDrawer']:
        game['currDrawer'] += 1
    game['order'].insert(insertPos, user)

def removeUser(game,user):
    game['players'].remove(user)
    if game['order'][game['currDrawer']] == user:
        nextUser(game, keepIndex = True)
    elif game['currDrawer'] > lst.index(user):
        game['currDrawer'] -= 1
    game['order'].remove(user)
    del game['points'][user]

def chooseWord(game, index):
    if type(index) != type(1) or index < 0 or index > 2:
        game['currWord'] = random.choice(game['offeredWords'])
    else:
        game['currWord'] = game['offeredWords']

def nextUser(game, keepIndex = False):
    if not(keepIndex): #Not executed if the current drawer is removed
        game['currDrawer'] += 1
    if game['currDrawer'] >= len(game['players']): #Increments round or ends game if all players have gone
        game['round'] += 1
        if game['round'] > game['maxRounds']:
            return 'Game End'
        game['currDrawer'] = 0
    game['offeredWords'] = random.sample(game['wordPool'], 3)