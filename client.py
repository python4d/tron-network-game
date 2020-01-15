# pylint: disable=no-member
import pygame
import pickle
from network import Network

from player import Player

# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
GREY =  (128,128,128)

pygame.font.init()

WIDTH=800
HEIGHT=800
win=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Client")

def server_error(n,txt=""):
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render("!Error %s : Vérifie ton serveur adr=%s, port=%s!" % (txt,*(n.addr)), 1, (200,255,200))
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
    win.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(8000)
    print("Couldn't get playerId - server problem?")

def dessin_scoring(win,p,score):
    pygame.draw.lines(win,p.color,True,((p.epaisseur,p.epaisseur),(WIDTH-p.epaisseur,p.epaisseur),(WIDTH-p.epaisseur,HEIGHT-p.epaisseur),(p.epaisseur,HEIGHT-p.epaisseur)),p.epaisseur)
    pygame.draw.lines(win,p.color,True,((p.epaisseur,p.epaisseur+HEIGHT/10),(WIDTH-p.epaisseur,p.epaisseur+HEIGHT/10)),p.epaisseur)
    pygame.draw.lines(win,p.color,True,((WIDTH/2-p.epaisseur,p.epaisseur),(WIDTH/2-p.epaisseur,HEIGHT/10+p.epaisseur)),p.epaisseur)
    
    font = pygame.font.SysFont("comicsansms", 80)
    text = font.render(str(score[0]), 1, (250,10,10))
    text_rect = text.get_rect(center=(WIDTH/4, HEIGHT/17))
    win.blit(text, text_rect)
    text = font.render(str(score[1]), 1, (10,10,250))
    text_rect = text.get_rect(center=(WIDTH*3/4, HEIGHT/17))
    win.blit(text, text_rect)

    


# Ecran du début avant connection
def startmenu(cr=0,cc=5):
    win.fill((128,128,128))
    win.set_alpha(cr)
    cr+=cc
    if cr>255 : 
        cr=255;cc=-cc
    elif cr<0 : 
        cr=0;cc=-cc
    font = pygame.font.SysFont("comicsansms", 30)
    text = font.render("Tape sur la barre d'espace pour rentrer dans TRON !", 1, (cr,cr,cr))
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2-100))
    win.blit(text, text_rect)    
    keys=pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:   
        # Création de l'objet Network déclenche la connexion
        #  et dans le thread/serveur.py envoie le n° du player  
        n = Network()
        try:
            playerId = int(n.getP())
        except:
            server_error(n,"n.getP()")
            return startmenu,[]            
        print("Tu es le Joueur", playerId)
        players=[Player(0),Player(1)]
        try:
            game = n.send(playerId)
        except:
            server_error(n,"n.send(playerId)")
            return startmenu,[]               
        return waitplayer,[n,game,players,playerId]
    return startmenu,[cr,cc]

#Ecran en attente d'un autre joueur game complète
def waitplayer(n,game,players,id):
    win.fill(GREY)
    font = pygame.font.SysFont("comicsans", 30)
    st="Vous êtes Joueur "+str(id)+","+" en haut à gauche" if id==0 else "en bas à droite"
    text = font.render(st, 1, BLACK)
    win.blit(text, (100,200))    
    st="...en attente du deuxième joueur..." if id==0 else "la partie va commencer !"
    text = font.render(st, 1, BLACK)
    win.blit(text, (100,300))  
    game = n.send(id)
    if game.bothWent():
        return ingame,[n,game,players,id]
    return waitplayer,[n,game,players,id]


def ingame(n,game,players,id):
    old_score=game.wins
    p=players[id]
    game=n.send(((p.x,p.y), p.angle, p.direction, p.collision))
    #print(game.moves)
    position_other_player=game.moves[(id+1)%2]
    if position_other_player!=None:
        players[(id+1)%2].trace.append(position_other_player[0])
        players[(id+1)%2].update_image(position_other_player[0],position_other_player[1])
        players[(id+1)%2].direction=position_other_player[2]
        players[(id+1)%2].collision=position_other_player[3]
        
        #print("trace 0:",players[0].trace,"\ntrace 1:",players[1].trace)
        if len(players[id].trace)<=len(players[(id+1)%2].trace):
            players[id].update()
        if len(players[id].trace)>=2 and len(players[(id+1)%2].trace)>=2:
            win.fill(GREY)
            win.blit(players[(id+1)%2].image, players[(id+1)%2].rect)
            win.blit(players[id].image, players[id].rect)
            for p in players:                
                pygame.draw.lines(win,p.color,False,p.trace,p.epaisseur)
            # encadrement noir et dessin scoring
            dessin_scoring(win,players[id],game.wins)
            players[id].collision=(players[id].get_color_front(win)==(0,0,0))
            if old_score!=game.wins: return gameover,[n,game,players,id]
            
    return ingame,[n,game,players,id]

def gameover(n,game,players,id):
    game = n.send("reset")
    players=[Player(0),Player(1)]
    return ingame,[n,game,players,id]


clock = pygame.time.Clock()
func,args = startmenu,[]
while True:
    clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
# State Machine => lance la fonction "func" avec les arguments "*args" 
# et récupére la prochaine "state" défini par une fonction et ses arguments...
    func,args = func(*args)
    pygame.display.flip()
