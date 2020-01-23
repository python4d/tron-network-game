# pylint: disable=no-member
import pygame
import pickle
import random
from network import Network

from player import Player,InputBox

# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
GREY =  (128,128,128)

pygame.font.init()

FRAMES=30
WIDTH=1200
HEIGHT=800
win=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Client")

prix=(("t'es nul...","perdu...","pas doué...","arrête frère !","le boulet...","t'as ton permis?","reste au lit", "regarde l'écran !","cas désespéré..."), \
    ("Joli !","Gagné !","Grand Pilote !","Excellent !","Bien Joué !","Beau Gosse !"))

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
    text = font.render(str(100-score[0]), 1, (250,10,10))
    text_rect = text.get_rect(center=(WIDTH/4, HEIGHT/17))
    win.blit(text, text_rect)
    text = font.render(str(100-score[1]), 1, (10,10,250))
    text_rect = text.get_rect(center=(WIDTH*3/4, HEIGHT/17))
    win.blit(text, text_rect)

    


# Ecran du début avant connection
def startmenu(events,cr=0,cc=5,input_box=InputBox(WIDTH, HEIGHT, 140, 32, text="192.168.0.9")):
    input_box.set_events(events)
    win.fill((128,128,128))
    win.set_alpha(cr)
    cr+=cc
    if cr>255 : 
        cr=255;cc=-cc
    elif cr<0 : 
        cr=0;cc=-cc
    font = pygame.font.SysFont("comicsansms", 30)
    text = font.render("Tape sur la barre d'espace pour rentrer dans TRON !" if input_box.active==False else "Modifie l'adresse du server et valide avec <Return>" , 1, (cr/3,cr,cr/2))
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2-100))
    win.blit(text, text_rect)    

    input_box.handle_event()
    input_box.update()
    input_box.draw(win)
    
    keys=pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and input_box.active==False:   
        # Création de l'objet Network déclenche la connexion
        #  et dans le thread/serveur.py envoie le n° du player          
        n = Network(server=input_box.text)
        try:
             playerId = int(n.getP())
        except:
            server_error(n,"n.getP()")
            return startmenu,[events]            
        print("Tu es le Joueur", playerId)
        players=[Player(0),Player(1)]
        try:
            game = n.send(playerId)
        except:
            server_error(n,"n.send(playerId)")
            return startmenu,[events]               
        return waitplayer,[n,game,players,playerId,0]
    return startmenu,[events,cr,cc,input_box]

#Ecran en attente d'un autre joueur game complète
def waitplayer(n,game,players,id,time=0):
    win.fill(GREY)
    font = pygame.font.SysFont("comicsansms", 50)
    st="Vous êtes le Joueur %i,"%(id)
    st+=" en haut à gauche" if id==0 else " en bas à droite"
    text = font.render(st, 1, BLACK)
    win.blit(text, text.get_rect(center=(WIDTH/2, HEIGHT/2-100)))   
    game = n.send(id)
    if game.bothWent():
        time+=1
        st= "la partie va commencer dans %1.1f s.!"% (5-float(time)/float(FRAMES))
        if time>FRAMES*5:
            return ingame,[n,game,players,id]
    else: 
        st="...en attente du deuxième joueur..." 
    text = font.render(st, 1, BLACK)
    win.blit(text, text.get_rect(center=(WIDTH/2, HEIGHT/2+100)))  
    game = n.send(id)
    return waitplayer,[n,game,players,id,time]


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
            if old_score!=game.wins: 
                return gameover,[n,game,players,id,old_score,0]
            
    return ingame,[n,game,players,id]

def gameover(n,game,players,id,old_score,time=0,str_prix=("","")):
    if time==0:
        players=[Player(0),Player(1)]
        time+=1
        return gameover,[n,game,players,id,old_score,time,(random.choice(prix[0]),random.choice(prix[1]))]
    elif time<2*FRAMES:
        game = n.send("reset")
        winner=0 if old_score[0]==game.wins[0] else 1 if old_score[1]==game.wins[1] else -1
        win.fill(GREY)
        win.blit(players[(id+1)%2].image, players[(id+1)%2].rect)
        win.blit(players[id].image, players[id].rect)
        dessin_scoring(win,players[id],game.wins)
        font = pygame.font.SysFont("comicsansms", 100)
        text = font.render(str_prix[1], 1, (10,250,10)) if winner==id else font.render(str_prix[0], 1, (250,10,10)) if winner!=-1 else font.render("Egalité !", 1, (10,10,250))
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        win.blit(text, text_rect)  
        font = pygame.font.SysFont("comicsansms", 30)
        text = font.render("Attention prochaine manche dans %1.1f s." % (2-float(time)/float(FRAMES)), 1, (10,10,250))
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2+300))
        win.blit(text, text_rect)  
        time+=1  
        return gameover,[n,game,players,id,old_score,time,str_prix]
    return ingame,[n,game,players,id]


clock = pygame.time.Clock()
events=[]
func,args = startmenu,[events]
while True:
    clock.tick(FRAMES)
    if pygame.event.peek(pygame.QUIT,True):
        raise SystemExit
    events.clear()
    events.extend(pygame.event.get())
# State Machine => lance la fonction "func" avec les arguments "*args" 
# et récupére la prochaine "state" défini par une fonction et ses arguments...
    func,args = func(*args)
    pygame.display.flip()
