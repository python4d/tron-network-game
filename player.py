# pylint: disable=no-member
import pygame


class Player(pygame.sprite.Sprite):
    
    def __init__(self, playerId=0,  color=(0,0,0), width=100, height=50, epaisseur=5):
        """ Graphic Sprite Constructor. """
        # Call the parent class (Sprite) constructor
        super(Player,self).__init__()

        self.playerId = playerId # soit 0 ou 1 pour le premier ou le deuxième arrivé sur le serveur 

        self.color = color
        self.collision = False
        self.width = width
        self.height = height
        self.epaisseur = epaisseur

        self.direction=(1,0) if playerId==0 else (-1,0) 

        # Load the image
        self.image = pygame.image.load(u"car.png").convert_alpha() if playerId==0 \
            else pygame.image.load(u"car1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(self.width,self.height))
        self.image_originale=self.image
        self.angle = 180 if playerId==0 else 0
        self.image = pygame.transform.rotate(self.image_originale,self.angle)
        

        # Set our transparent color
        self.image.set_colorkey(self.color)
        
        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect().move((50,50) if playerId==0 else (500,500))
        self.x=self.rect.centerx
        self.y=self.rect.centery
        self.trace=[(self.x,self.y)]

        self.vel = 5

    def get_color_front(self,win):
        c=(128,128,128)
        try:
            c=win.get_at((self.x+self.direction[0],self.y+self.direction[1]))[0:-1]
        except:
            pass
        return c

    def set_trace(self,trace):
        self.trace=trace
        return trace

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.angle!=180:
            self.direction=(-1,0)
            self.angle=0

        elif keys[pygame.K_RIGHT] and self.angle!=0:
            self.direction=(1,0)
            self.angle=180

        elif keys[pygame.K_UP] and self.angle!=90:
            self.direction=(0,-1)
            self.angle=-90

        elif keys[pygame.K_DOWN] and self.angle!=-90:
            self.angle=90
            self.direction=(0,1)
        
        self.x += int(self.vel*self.direction[0]/5)*5
        self.y += int(self.vel*self.direction[1]/5)*5
        self.trace.append((self.x,self.y))

        self.update_image((self.x,self.y),self.angle)

    def update_image(self,pos,angle):
        self.image = pygame.transform.rotate(self.image_originale,angle)
        self.rect = self.image.get_rect(center= pos)