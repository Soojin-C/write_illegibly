from flask_socketio import SocketIO, join_room, leave_room, emit, send
from flask import Flask, render_template, request
import threading
import os

from util import word
from util import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
socketio = SocketIO(app)

continueTimer = True
timerTime = 60 #Timer to be displayed
rooms = {} #request.sid : roomID
games = {} #roomID : game info dictionary

@app.before_first_request #Executed upon startup
def setup():
    countdown() #Start countdown timer

@app.route("/")
def root():
    return render_template("index.html", currTime = timerTime)

@app.route("/game", methods=["GET", "POST"])
def game():
    return render_template("game.html")

@socketio.on("joinRoom")
def joinRoom(roomID):
    if len(roomID) == 0:
        return
    if request.sid in rooms: #Checks if the user is already in a room
        if rooms[request.sid] == roomID:
            return
        leave_room(rooms[request.sid])
        if len(games[rooms[request.sid]]['players']) == 0: #Deletes game room if no-one is in it
            games.remove(rooms[request.sid])
    join_room(roomID) #Places user in a room
    if roomID not in games: #Create new game
        games[roomID] = Game.newGame(request.sid)
        emit('yourturn')
    else:
        Game.addUser(games[roomID],request.sid)
    rooms[request.sid] = roomID #Sets room of user in a dictionary for later use
    emit('joinRoom', roomID)

@socketio.on('disconnect')
def disconn(): #Executed when a client disconnects from the server
    if request.sid in rooms:
        Game.removeUser(games[rooms[request.sid]], request.sid)
        if len(games[rooms[request.sid]]['players']) == 0: #Deletes game room if no-one is in it
            games.pop(rooms[request.sid])
        rooms.pop(request.sid)

@socketio.on('requestLines')
def returnLines(data):
    emit('recieveLines', games[rooms[request.sid]]['currLines'])

@socketio.on('clearBoard')
def clearBoard(data):
    games[rooms[request.sid]]['currLines'] = []
    # print(currLines)
    emit('clearBoard', None, broadcast = True, include_self = False, room = rooms[request.sid])

@socketio.on('newLine')
def newLine(line):
    currGame = games[rooms[request.sid]]
    # print(currGame['order'], currGame['currDrawer'])
    if (request.sid != currGame['order'][currGame['currDrawer']]):
        return
    games[rooms[request.sid]]['currLines'].append(line);
    # print(line);
    emit('newLine', line, broadcast = True, include_self = False, room = rooms[request.sid])

def countdown():
    global continueTimer, timerTime
    if continueTimer:
        threading.Timer(1, countdown).start()
        #Execute the following tasks every second
        for roomID in games:
            games[roomID]['timerTime'] -= 1
            if games[roomID]['timerTime'] <= -1:
                games[roomID]['timerTime'] = games[roomID]['maxTime']
                socketio.emit('notyourturn', room = games[roomID]['order'][games[roomID]['currDrawer']])
                Game.nextUser(games[roomID])
                socketio.emit('yourturn', room = games[roomID]['order'][games[roomID]['currDrawer']])
            # print(games[roomID]['timerTime'])
            socketio.emit('updateTimer', games[roomID]['timerTime'], room = roomID)


@socketio.on('message')
def message(msg, methods=['GET','POST']):
    #print("Message " + msg)
    global currWord # TESTING
    currWord = word.randword() # TESTING
    if len(msg) != 0:
        send(msg, broadcast=True)
        guess = msg
        print(guess == currWord)
        if guess == currWord:
            send("Correct")


#@socketio.on("eventName")
#def fxn(data):
#   <Stuff to do upon recieving event>

if __name__ == '__main__':
    socketio.run(app, debug = True)
