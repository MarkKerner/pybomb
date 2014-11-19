import pygame
from random import randint
import time


pygame.init()

ekraani_pind = pygame.display.set_mode((855, 675))
pygame.display.set_caption("Pymberman")
plokk = pygame.image.load("plokk.png")
põrand = pygame.image.load("floor1.png")
sein = pygame.image.load("seinedges.png")
pommipilt = pygame.image.load("pomm.png")
plahvatuspilt = pygame.image.load("plahvatus.png")


ekraani_pind.blit(põrand, (0, 0))  # Joonistan põranda


ruudukülg = 45
seinad = []
plokid = []
pommikoordinaadid = []

x = 1
y = 1
moveX = ruudukülg
moveY = ruudukülg

#def leia_ruudu_koordinaadid(x, y):
#    ruutX = x // 45 #Proovi siin x - (mingi asi), et oleks lisaruum
#    ruutY = y // 45
#    return (int(ruutX), int(ruutY))

#def piiridest_väljas(x, y):
#    
#    koordinaadid = (ruutX*45, ruutY*45)
#    if koordinaadid in plokid or koordinaadid in seinad or koordinaadid in pommikoordinaadid:
#        return True
#    else:
#        return False

for i in range(19):  # Lisan plokid ja seinad listidesse
    for j in range(15):
        if i == 0 or i == 18:
            plokid.append((i*ruudukülg, j*ruudukülg))
        else:
            if i % 2 == 0 and j % 2 == 0:
                plokid.append((i*ruudukülg, j*ruudukülg))
            elif j == 0 or j == 14:
                plokid.append((i*ruudukülg, j*ruudukülg))
            else:
                if randint(1, 9) < 8 and not ((i == 1 or i == 17) and (j < 4 or j > 10) or (j == 1 or j == 13) and (i < 4 or i > 13)):
                    seinad.append((i*ruudukülg, j*ruudukülg))

for plokkXY in plokid:  # Joonistan plokid
    ekraani_pind.blit(plokk, plokkXY)
for seinXY in seinad:  # Joonistan seinad
    ekraani_pind.blit(sein, seinXY)


class PyBomber:
    def __init__(self, x, y, pilt1, pilt2):
        self.x = x
        self.y = y
        self.sprite1 = pygame.image.load(pilt1)
        self.sprite2 = pygame.image.load(pilt2)
        self.sprite = self.sprite1
        self.maxpommid = 3
        self.pommitugevus = 2
        self.pommid = []
        self.loend = 0  # Loeb programmi kordusi piltide vahetuseks
        
    def uuenda(self):
        self.oota_pauku()
        
        ekraani_pind.blit(self.sprite, (self.x, self.y))
        self.loend += 1
        if self.loend >= 20:
            if self.sprite == self.sprite1:
                self.sprite = self.sprite2
            else:
                self.sprite = self.sprite1
            self.loend = 0
        
    def aseta_pomm(self):
        if len(self.pommid) < self.maxpommid:
            self.pommid.append(Pomm(self.x, self.y, self.pommitugevus))
            pommikoordinaadid.append((self.x, self.y))
    def oota_pauku(self):
        for pomm in self.pommid:
            pomm.uuenda()
            if pomm.olek == "plahvatanud":
                pommikoordinaadid.remove((pomm.x, pomm.y))
                self.pommid.remove(pomm)
                
        
sinine = PyBomber(45, 90, "sinine_esi.png", "sinine_esi_2.png")


class Pomm:
    def __init__(self, x, y, pommitugevus):
        self.x = x
        self.y = y
        self.algusaeg = time.time() # AEG
        self.pommitugevus = pommitugevus
        self.olek = "ootel"
        self.plahvatuskohad = [] # Siia listi lisan kohad, kuhu pommi lõhkemine ulatub
        
    def uuenda(self):
        if self.olek == "ootel":
            ekraani_pind.blit(pommipilt, (self.x, self.y))
            
            if time.time() - self.algusaeg >= 3:
                self.plahvatus()
                self.algusaeg = time.time()
                self.plahvatuskohad.append((self.x, self.y))
        elif self.olek == "plahvatamas":
            if time.time() - self.algusaeg <= 1.5:
                for plahvatuskoht in self.plahvatuskohad:
                    ekraani_pind.blit(plahvatuspilt, plahvatuskoht)
            else:
                self.olek = "plahvatanud"
  
    def plahvatus(self):
        self.olek = "plahvatamas"
        if (self.x + 45, self.y) in seinad: # Plahvatuse suund - PAREMALE
            seinad.remove((self.x + 45, self.y))
            self.plahvatuskohad.append((self.x + 45, self.y))
            
        elif (self.x + 45, self.y) not in plokid: # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x + 45, self.y))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x + (i+2)*45, self.y))
                if (self.x + (i+2)*45, self.y) in seinad:
                    seinad.remove((self.x + (i+2)*45, self.y))
                    break
                
        if (self.x - 45, self.y) in seinad: # Plahvatuse suund - VASAKULE
            self.plahvatuskohad.append((self.x - 45, self.y))
            seinad.remove((self.x - 45, self.y))
            
        elif (self.x - 45, self.y) not in plokid: # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x - 45, self.y))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x - (i+2)*45, self.y))
                if (self.x - (i+2)*45, self.y) in seinad:
                    seinad.remove((self.x - (i+2)*45, self.y))
                    break
                
        if (self.x, self.y + 45) in seinad: # Plahvatuse suund - ALLA
            seinad.remove((self.x, self.y + 45))
            self.plahvatuskohad.append((self.x, self.y + 45))
            
        elif (self.x, self.y + 45) not in plokid: # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x, self.y + 45))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x, self.y + (i+2)*45))
                if (self.x, self.y + (i+2)*45) in seinad:
                    seinad.remove((self.x, self.y + (i+2)*45))
                    break
                
        if (self.x, self.y - 45) in seinad: # Plahvatuse suund - ÜLES
            seinad.remove((self.x, self.y - 45))
            self.plahvatuskohad.append((self.x, self.y - 45))
        elif (self.x, self.y - 45) not in plokid: # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x, self.y - 45))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x, self.y - (i+2)*45))
                if (self.x, self.y - (i+2)*45) in seinad:
                    seinad.remove((self.x, self.y - (i+2)*45))
                    break
                
                    

sinine.uuenda()

pygame.display.flip() # Joonistab pildi


clock = pygame.time.Clock()

while True:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        break
    elif event.type == pygame.KEYDOWN: # Klaviatuuri nuppude vajutamine
        
        if event.key == pygame.K_UP:
            if (sinine.x , sinine.y - 45) not in plokid and (sinine.x , sinine.y - 45) not in seinad and (sinine.x, sinine.y - 45) not in pommikoordinaadid:
                sinine.y -= moveY
        if event.key == pygame.K_DOWN:
            if (sinine.x , sinine.y + 45) not in plokid and (sinine.x , sinine.y + 45) not in seinad and (sinine.x, sinine.y + 45) not in pommikoordinaadid:
                sinine.y += moveY
        if event.key == pygame.K_RIGHT:
            if (sinine.x + 45, sinine.y) not in plokid and (sinine.x + 45, sinine.y) not in seinad and (sinine.x + 45, sinine.y) not in pommikoordinaadid:
                sinine.x += moveX
        if event.key == pygame.K_LEFT:
            if (sinine.x - 45, sinine.y) not in plokid and (sinine.x - 45, sinine.y) not in seinad and (sinine.x - 45, sinine.y) not in pommikoordinaadid:
                sinine.x -= moveX
        if event.key == pygame.K_SPACE:
            sinine.aseta_pomm()

    ekraani_pind.fill((0, 0, 0))  # Puhastan ekraani

    ekraani_pind.blit(põrand, (0, 0))  # Joonistan põranda

    sinine.uuenda()
    
    for plokkXY in plokid:  # Joonistan plokid
        ekraani_pind.blit(plokk, plokkXY)
    for seinXY in seinad:  # Joonistan seinad
        ekraani_pind.blit(sein, seinXY)
    
    pygame.display.flip()  # Loon uue pildi
    clock.tick(60)
    
pygame.quit()
