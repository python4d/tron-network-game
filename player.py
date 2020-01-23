# pylint: disable=no-member
import pygame
class InputBox:
    def __init__(self, x, y, w, h,text=''):
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.COLOR_ACTIVE = pygame.Color('purple4')
        self.FONT = pygame.font.Font(None, 32)
        self.rect = pygame.Rect(x, y/3*2, w, h)
        self.maxx = x
        self.maxy = y
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.text_first=text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False
        self.events=[]

    @staticmethod
    def validate_ip(s):
        a = s.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def set_events(self,e):
        self.events=e

    def handle_event(self):
        print(self.events)
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        print(self.text)
                        if not InputBox.validate_ip(self.text):
                            self.text=self.text_first
                        self.active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        if event.unicode in ['0','1','2','3','4','5','6','7','8','9','.']:
                            self.text += event.unicode
                        

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
        self.rect.x = (self.maxx-width)/2

    def draw(self, screen):        
        # Change the current color of the input box.
        self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        # Re-render the text.
        self.txt_surface = self.FONT.render("Pour modifier l'adresse du server, clique dessus ="+self.text, True, self.color)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Player(pygame.sprite.Sprite):
    def __init__(self, playerId=0, screenW=1200, screenH=800,  width=50, height=25, color=(0,0,0), epaisseur=10):
        """ Graphic Sprite Constructor. """
        # Call the parent class (Sprite) constructor
        super(Player,self).__init__()

        self.playerId = playerId # soit 0 ou 1 pour le premier ou le deuxième arrivé sur le serveur 

        self.epaisseur = epaisseur
        self.color = color #couleur de détection murs
        self.collision = False
        self.width = width
        self.height = height
        self.screenW=screenW
        self.screenH=screenH

        self.direction=(1,0) if playerId==0 else (-1,0) 

        # Chargement des images des voitures suivant player0 ou player1
        self.image = pygame.image.load(u".\\car.png").convert_alpha() if playerId==0 \
            else pygame.image.load(u".\\car1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(self.width,self.height))
        self.image_originale=self.image
        self.angle = 180 if playerId==0 else 0
        self.image = pygame.transform.rotate(self.image_originale,self.angle)
        # Set our transparent color
        self.image.set_colorkey(self.color) #couleur noir de détection des murs
        # Fetch the rectangle object that has the dimensions of the image 'image'.
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect().move((100,self.screenH/10*2) \
                            if playerId==0 else (self.screenW-100-width,self.screenH/10*8))
        self.x=self.rect.centerx
        self.y=self.rect.centery
        self.trace=[(self.x,self.y)]
        # déplacemet/grille de jeu
        self.vel = 10

    def get_color_front(self,win):
        c=(128,128,128)
        try:
            c=win.get_at((self.x+self.direction[0],self.y+self.direction[1]))[0:-1]
        except:
            c=self.color
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
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            speed=2
        else:
            speed=1

        self.x += int(self.direction[0])*self.vel*speed
        self.y += int(self.direction[1])*self.vel*speed
        self.trace.append((self.x,self.y))

        self.update_image((self.x,self.y),self.angle)

    def update_image(self,pos,angle):
        self.image = pygame.transform.rotate(self.image_originale,angle)
        self.rect = self.image.get_rect(center= pos)