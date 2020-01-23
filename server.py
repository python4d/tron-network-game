import socket
from _thread import start_new_thread
import pickle
from game import Game

def get_ips():
    try:
        #https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        ips=(([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or \
        [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])
    except socket.error as e:
        print (str(e))
    return ips

def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p))) #Envoi le numéro du joueur
    #print ((p,"# conn.send(str.encode(str(p)))"))
    while True:
        try:
            #data = conn.recv(4096).decode()
            data = pickle.loads(conn.recv(2048*2))
            #print(p,"data = pickle.loads(conn.recv(2048*2))",data)
            if gameId in games:
                game = games[gameId]

                if data==None: #rien recu problem!
                    break
                else: 
                    if data == "reset":
                        game.resetMove()
                        print(p,"# game.resetWent()")
                    elif data == 0 or data == 1:
                        game.play(p, data)
                        #print(p,"#game.play (p,data)",data)
                    else:
                        #print(p,"game.set_player_move(p,data)",data)
                        game.set_player_move(p,data)
                    conn.sendall(pickle.dumps(game)) 
                    #print(p,"#conn.sendall(pickle.dumps(game)")
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()

# Récupération de la première IP local
server = get_ips()[0]
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)
try:
    s.listen(2)
except socket.error as e:
    str(e)    
print("Waiting for a connection, Server Started on (%s:%s)" % (server,port))

connected = set()
games = {}
idCount = 0

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1)//2
    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game n°"+str(gameId))
    else:
        games[gameId].ready = True
        p = 1

    start_new_thread(threaded_client, (conn, p, gameId))