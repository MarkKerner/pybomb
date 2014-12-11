import pygame
from random import randint
import pygame.locals
import socket
import select
import random
import time
import json

pygame.init()


ekraani_pind = pygame.display.set_mode((855, 675))
pygame.display.set_caption("Pymberman")
plokk = pygame.image.load("plokk.png")
põrand = pygame.image.load("floor1.png")
põrand = põrand.convert()
sein = pygame.image.load("seinedges.png")
pommipilt = pygame.image.load("bombonfire.png")
plahvatuspilt = pygame.image.load("plahvatus.png")
adikets = pygame.image.load("adidasspeed.png")
tuumapomm = pygame.image.load("tuumapomm.png")
lisapomm = pygame.image.load("bomb.png")

ekraani_pind.blit(põrand, (0, 0))  # Joonistan põranda

ruudukülg = 45
pommikoordinaadid = []
boonused = []
mängijad = []
seinad = []
plokid = []

addr = "127.0.0.1"
serverport = 9009
clientport = random.randrange(8000, 8999)
conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
conn.bind(("127.0.0.1", clientport))
read_list = [conn]
write_list = []

def leia_ruut(x, y):  # Leiab ruudu koordinaadid, kus suurem osa pybomberist on
    if x % 45 >= 22.5:
        ruutX = (x // 45 + 1) * 45
    elif x % 45 < 22.5 and x % 45 != 0:
        ruutX = (x // 45) * 45
    else:
        ruutX = x

    if y % 45 >= 22.5:
        ruutY = (y // 45 + 1) * 45
    elif y % 45 < 22.5 and y % 45 != 0:
        ruutY = (y // 45) * 45
    else:
        ruutY = y
    
    return (int(ruutX), int(ruutY))


def leia_koordinaadi_ruut(x, y):  # Leiab ruudu, kus antud koordinaadid paiknevad
    ruutX = (x // 45) * 45
    ruutY = (y // 45) * 45
    return (int(ruutX), int(ruutY))


def loo_boonus(x, y):
    number = randint(1, 3)
    if number == 1:
        boonused.append(Boonus(x, y, "speed"))
    elif number == 2:
        boonused.append(Boonus(x, y, "power"))
    else:
        boonused.append(Boonus(x, y, "extrabomb"))


def lisa_uus_mängija():
    if len(mängijad) < 1:
        mängijad.append(PyBomber(45, 45, "sinine"))   
    elif len(mängijad) < 2:
        mängijad.append(PyBomber(765, 585, "punane"))
    elif len(mängijad) < 3:
        mängijad.append(PyBomber(45, 585, "roheline"))
    elif len(mängijad) < 4:
        mängijad.append(PyBomber(765, 45, "kollane"))


def joonista_maailm(plokid, seinad):
    for plokkXY in plokid:  # Joonistan plokid
        ekraani_pind.blit(plokk, plokkXY)
    for seinXY in seinad:  # Joonistan seinad
        ekraani_pind.blit(sein, seinXY)


class PyBomber:
    def __init__(self, x, y, värv):
        self.x = x
        self.y = y
        self.koruutX = 0
        self.koruutY = 0
        self.ruutX = 0
        self.ruutY = 0
        self.värv = värv
        self.speed = 5  # Liikumiskiirus
        self.suundX = ""  # Suund x-teljel
        self.suundY = ""  # Suund y-teljel
        self.kahevahelX = False
        self.kahevahelY = False
        self.spritesuund = "esi"
        self.liigub = False
        self.maxpommid = 1
        self.pommitugevus = 2
        self.pommid = []
        self.elus = True
        self.loend = 0  # Loeb programmi kordusi piltide vahetuseks
        self.esi1 = ""
        self.esi2 = ""
        self.parem1 = ""
        self.parem2 = ""
        self.parem3 = ""
        self.parem4 = ""
        self.vasak1 = ""
        self.vasak2 = ""
        self.vasak3 = ""
        self.vasak4 = ""
        self.tagu1 = ""
        self.tagu2 = ""
        self.sprite1 = ""
        self.sprite2 = ""
        self.sprite3 = ""
        self.sprite4 = ""
        self.pildid()
        self.sprite = self.sprite1

    def pildid(self):
        self.esi1 = pygame.image.load(self.värv + "/" + "esi_1.png")
        self.esi2 = pygame.image.load(self.värv + "/" + "esi_2.png")
        self.parem1 = pygame.image.load(self.värv + "/" + "parem_1.png")
        self.parem2 = pygame.image.load(self.värv + "/" + "parem_2.png")
        self.parem3 = pygame.image.load(self.värv + "/" + "parem_3.png")
        self.parem4 = pygame.image.load(self.värv + "/" + "parem_4.png")
        self.vasak1 = pygame.image.load(self.värv + "/" + "vasak_1.png")
        self.vasak2 = pygame.image.load(self.värv + "/" + "vasak_2.png")
        self.vasak3 = pygame.image.load(self.värv + "/" + "vasak_3.png")
        self.vasak4 = pygame.image.load(self.värv + "/" + "vasak_4.png")
        self.tagu1 = pygame.image.load(self.värv + "/" + "tagu_1.png")
        self.tagu2 = pygame.image.load(self.värv + "/" + "tagu_2.png")
        self.sprite1 = self.esi1
        self.sprite2 = self.esi2

    def liigu(self):
        (self.ruutX, self.ruutY) = leia_ruut(self.x, self.y)
        (self.koruutX, self.koruutY) = leia_koordinaadi_ruut(self.x, self.y)

        if self.suundX == "right":  # Kui on vajutatud paremale

            if self.ruutX == self.x and self.ruutY != self.y:  # Kui pybomber on liikumas üles või alla

                if 45 < self.y % 90 < 85:  # Kui pybomber on ruudukeskmest ülevalpool

                    if (self.koruutX + 45, self.koruutY) not in plokid and (self.koruutX + 45, self.koruutY) not in seinad and (self.koruutX + 45, self.koruutY) not in pommikoordinaadid:
                        self.spritesuund = "tagu"
                        if self.y - self.speed < self.koruutY:  # Liigub üles
                            self.y = self.koruutY
                        else:
                            self.y -= self.speed
                            
                elif 5 < self.y % 90 < 45:  # Kui pybomber on ruudukeskmest allpool

                    if (self.koruutX + 45, self.koruutY + 45) not in plokid and (self.koruutX + 45, self.koruutY) not in seinad and (self.koruutX + 45, self.koruutY) not in pommikoordinaadid:
                        self.spritesuund = "esi"
                        if self.y + self.speed > self.koruutY + 45:  # Liigub alla

                            self.y = self.koruutY + 45
                        else:
                            self.y += self.speed

            else:   # Kui pybomber on liikumas paremale või vasakule (või on ruudu keskel)
                self.spritesuund = "parem"
                if self.x != self.ruutX:
                    if self.x + self.speed > self.koruutX + 45:    # Liigub paremale
                        self.x = self.koruutX + 45
                    else:
                        self.x += self.speed
                else:
                    print(plokid)
                    print(seinad)
                    if (self.x + 45, self.ruutY) not in plokid and (self.x + 45, self.ruutY) not in seinad and (self.x + 45, self.ruutY) not in pommikoordinaadid:
                        self.x += self.speed

        elif self.suundX == "left":  # Kui on vajutatud vasakule

            if self.ruutX == self.x and self.ruutY != self.y:  # Kui pybomber on liikumas üles või alla

                if 45 < self.y % 90 < 85:  # Kui pybomber on ruudukeskmest ülevalpool

                    if (self.koruutX - 45, self.koruutY) not in plokid and (self.koruutX - 45, self.koruutY) not in seinad and (self.koruutX - 45, self.koruutY) not in pommikoordinaadid:
                        self.spritesuund = "tagu"
                        if self.y - self.speed < self.koruutY:  # Liigub üles
                            self.y = self.koruutY
                        else:
                            self.y -= self.speed

                elif 5 < self.y % 90 < 45:  # Kui pybomber on ruudukeskmest allpool

                    if (self.koruutX - 45, self.koruutY - 45) not in plokid and (self.koruutX - 45, self.koruutY - 45) not in seinad and (self.koruutX - 45, self.koruutY - 45) not in pommikoordinaadid:
                        self.spritesuund = "esi"
                        if self.y + self.speed > self.koruutY + 45:  # Liigub alla
                            self.y = self.koruutY + 45
                        else:
                            self.y += self.speed

            else:   # Kui pybomber on liikumas paremale või vasakule (või on ruudu keskel)
                self.spritesuund = "vasak"
                if self.x != self.ruutX:
                    if self.x - self.speed < self.koruutX:    # Liigub vasakule
                        self.x = self.koruutX
                    else:
                        self.x -= self.speed
                else:
                    if (self.ruutX - 45, self.ruutY) not in plokid and (self.ruutX - 45, self.ruutY) not in seinad and (self.ruutX - 45, self.ruutY) not in pommikoordinaadid:
                        self.x -= self.speed

        elif self.suundY == "up":  # Kui on vajutatud üles

            if self.ruutX != self.x and self.ruutY == self.y:  # Kui pybomber on liikumas paremale või vasakule

                if 45 < self.x % 90 < 85:  # Kui pybomber on ruudukeskmest vasakul

                    if (self.koruutX, self.koruutY - 45) not in plokid and (self.koruutX, self.koruutY - 45) not in seinad and (self.koruutX, self.koruutY - 45) not in pommikoordinaadid:
                        self.spritesuund = "vasak"
                        if self.x - self.speed < self.koruutX:  # Liigub vasakule
                            self.x = self.koruutX
                        else:
                            self.x -= self.speed

                elif 5 < self.x % 90 < 45:  # Kui pybomber on ruudukeskmest paremal

                    if (self.koruutX + 45, self.koruutY - 45) not in plokid and (self.koruutX + 45, self.koruutY - 45) not in seinad and (self.koruutX + 45, self.koruutY - 45) not in pommikoordinaadid:
                        self.spritesuund = "parem"
                        if self.x + self.speed > self.koruutX + 45:  # Liigub paremale
                            self.x = self.koruutX + 45
                        else:
                            self.x += self.speed
                            
            else:  # Kui pybomber on liikumas üles või alla (või on ruudu keskel)
                self.spritesuund = "tagu"
                if self.y != self.ruutY:
                    if self.y - self.speed < self.koruutY:    # Liigub üles
                        self.y = self.koruutY
                    else:
                        self.y -= self.speed
                else:
                    if (self.ruutX, self.y - 45) not in plokid and (self.ruutX, self.y - 45) not in seinad and (self.ruutX, self.y - 45) not in pommikoordinaadid:
                        self.y -= self.speed

        elif self.suundY == "down":  # Kui on vajutatud alla

            if self.ruutX != self.x and self.ruutY == self.y:  # Kui pybomber on liikumas paremale või vasakule

                if 45 < self.x % 90 < 85:  # Kui pybomber on ruudukeskmest vasakul

                    if (self.koruutX, self.koruutY + 45) not in plokid and (self.koruutX, self.koruutY + 45) not in seinad and (self.koruutX, self.koruutY + 45) not in pommikoordinaadid:
                        self.spritesuund = "vasak"
                        if self.x - self.speed < self.koruutX:  # Liigub vasakule
                            self.x = self.koruutX
                        else:
                            self.x -= self.speed
                        
                elif 5 < self.x % 90 < 45:  # Kui pybomber on ruudukeskmest paremal

                    if (self.koruutX + 45, self.koruutY + 45) not in plokid and (self.koruutX + 45, self.koruutY + 45) not in seinad and (self.koruutX + 45, self.koruutY + 45) not in pommikoordinaadid:
                        self.spritesuund = "parem"
                        if self.x + self.speed > self.koruutX + 45:  # Liigub paremale
                            self.x = self.koruutX + 45
                        else:
                            self.x += self.speed

            else:  # Kui pybomber on liikumas üles või alla (või on ruudu keskel)
                self.spritesuund = "esi"
                if self.y != self.ruutY:
                    if self.y + self.speed > self.koruutY + 45:    # Liigub alla
                        self.y = self.koruutY + 45
                    else:
                        self.y += self.speed
                else:
                    if (self.ruutX, self.y + 45) not in plokid and (self.ruutX, self.y + 45) not in seinad and (self.ruutX, self.y + 45) not in pommikoordinaadid:
                        self.y += self.speed

        if self.suundX != "" or self.suundY != "":
            self.liigub = True
            if self.spritesuund == "esi":
                self.sprite1 = self.esi1
                self.sprite2 = self.esi2
            elif self.spritesuund == "tagu":
                self.sprite1 = self.tagu1
                self.sprite2 = self.tagu2
            elif self.spritesuund == "parem":
                self.sprite1 = self.parem1
                self.sprite2 = self.parem2
                self.sprite3 = self.parem3
                self.sprite4 = self.parem4
            elif self.spritesuund == "vasak":
                self.sprite1 = self.vasak1
                self.sprite2 = self.vasak2
                self.sprite3 = self.vasak3
                self.sprite4 = self.vasak4
        else:
            self.liigub = False
            self.sprite1 = self.esi1
            self.sprite2 = self.esi2

    def uuenda(self):
        
        self.liigu()

        if self.liigub:
            self.loend += 1
            if self.spritesuund == "esi" or self.spritesuund == "tagu":
                if self.loend >= 10:
                    if self.sprite == self.sprite1:
                        self.sprite = self.sprite2
                    else:
                        self.sprite = self.sprite1
                    self.loend = 0
            else:
                if self.loend >= 5:
                    if self.sprite == self.sprite1:
                        self.sprite = self.sprite2
                    elif self.sprite == self.sprite2:
                        self.sprite = self.sprite3
                    elif self.sprite == self.sprite3:
                        self.sprite = self.sprite4
                    else:
                        self.sprite = self.sprite1
                    self.loend = 0

        for boonus in boonused:  # Kontrollin, kas pybomber on ühegi boonuse peal ja uuendan boonuseid
            boonus.uuenda()
            if not boonus.olemas:
                boonused.remove(boonus)
            elif leia_koordinaadi_ruut(self.x + 5, self.y + 5) == (boonus.x, boonus.y) or leia_koordinaadi_ruut(self.x + 40, self.y + 40) == (boonus.x, boonus.y):
                if boonus.boonus == "speed":
                    self.speed += 1
                elif boonus.boonus == "power":
                    self.pommitugevus += 1
                else:
                    self.maxpommid += 1
                boonused.remove(boonus)
            else:
                if boonus.boonus == "speed":
                    ekraani_pind.blit(adikets, (boonus.x, boonus.y))
                elif boonus.boonus == "power":
                    ekraani_pind.blit(tuumapomm, (boonus.x, boonus.y))
                else:
                    ekraani_pind.blit(lisapomm, (boonus.x, boonus.y))

        self.oota_pauku()
        
        if self.elus:
            ekraani_pind.blit(self.sprite, (self.x, self.y))  # Joonistan pybomberi
        
    def aseta_pomm(self):
        if len(self.pommid) < self.maxpommid:
            (self.ruutX, self.ruutY) = leia_ruut(self.x, self.y)
            self.pommid.append(Pomm(self.ruutX, self.ruutY, self.pommitugevus))
            pommikoordinaadid.append((self.ruutX, self.ruutY))

    def oota_pauku(self):
        for pomm in self.pommid:
            pomm.uuenda()
            if pomm.olek == "plahvatamas":  # Kontrollin, kas pybomber saab plahvatusega pihta
                for plahvatuskoht in pomm.plahvatuskohad:
                    if leia_koordinaadi_ruut(self.x + 5, self.y + 5) == plahvatuskoht or leia_koordinaadi_ruut(self.x + 40, self.y + 40) == plahvatuskoht:
                        self.elus = False
                    for ootavpomm in self.pommid:
                        if ootavpomm.olek == "ootel" and (ootavpomm.x, ootavpomm.y) == plahvatuskoht:
                            ootavpomm.algusaeg = -3

            if pomm.olek == "plahvatanud":
                pommikoordinaadid.remove((pomm.x, pomm.y))
                self.pommid.remove(pomm)
                

class Pomm:
    def __init__(self, x, y, pommitugevus):
        self.x = x
        self.y = y
        self.algusaeg = time.time()  # AEG
        self.pommitugevus = pommitugevus
        self.olek = "ootel"
        self.plahvatuskohad = []  # Siia listi lisan kohad, kuhu pommi lõhkemine ulatub
        
    def uuenda(self):
        if self.olek == "ootel":
            ekraani_pind.blit(pommipilt, (self.x, self.y))
            
            if time.time() - self.algusaeg >= 3:
                self.plahvatus()
                self.algusaeg = time.time()
    
        elif self.olek == "plahvatamas":
            if time.time() - self.algusaeg <= 1.5:
                for plahvatuskoht in self.plahvatuskohad:
                    ekraani_pind.blit(plahvatuspilt, plahvatuskoht)
    
            else:
                self.olek = "plahvatanud"
  
    def plahvatus(self):
        self.olek = "plahvatamas"
        self.plahvatuskohad.append((self.x, self.y))
        if (self.x + 45, self.y) in seinad:  # Plahvatuse suund - PAREMALE
            seinad.remove((self.x + 45, self.y))
            if randint(1, 10) < 4:  # Boonuse loomine
                loo_boonus(self.x + 45, self.y)
            self.plahvatuskohad.append((self.x + 45, self.y))
            
        elif (self.x + 45, self.y) not in plokid:  # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x + 45, self.y))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x + (i+2)*45, self.y))
                if (self.x + (i+2)*45, self.y) in seinad:
                    seinad.remove((self.x + (i+2)*45, self.y))
                    if randint(1, 10) < 4:  # Boonuse loomine
                        loo_boonus(self.x + (i+2)*45, self.y)
                    break
                
        if (self.x - 45, self.y) in seinad:  # Plahvatuqse suund - VASAKULE
            self.plahvatuskohad.append((self.x - 45, self.y))
            seinad.remove((self.x - 45, self.y))
            if randint(1, 10) < 4:  # Boonuse loomine
                loo_boonus(self.x - 45, self.y)
            
        elif (self.x - 45, self.y) not in plokid:  # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x - 45, self.y))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x - (i+2)*45, self.y))
                if (self.x - (i+2)*45, self.y) in seinad:
                    seinad.remove((self.x - (i+2)*45, self.y))
                    if randint(1, 10) < 4:  # Boonuse loomine
                        loo_boonus(self.x - (i+2)*45, self.y)
                    break
                
        if (self.x, self.y + 45) in seinad:  # Plahvatuse suund - ALLA
            seinad.remove((self.x, self.y + 45))
            if randint(1, 10) < 4:  # Boonuse loomine
                loo_boonus(self.x, self.y + 45)
            self.plahvatuskohad.append((self.x, self.y + 45))
            
        elif (self.x, self.y + 45) not in plokid:  # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x, self.y + 45))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x, self.y + (i+2)*45))
                if (self.x, self.y + (i+2)*45) in seinad:
                    seinad.remove((self.x, self.y + (i+2)*45))
                    if randint(1,10) < 4:  # Boonuse loomine
                        loo_boonus(self.x, self.y + (i+2)*45)
                    break
                
        if (self.x, self.y - 45) in seinad:  # Plahvatuse suund - ÜLES
            seinad.remove((self.x, self.y - 45))
            if randint(1,10) < 4:  # Boonuse loomine
                loo_boonus(self.x, self.y - 45)
            self.plahvatuskohad.append((self.x, self.y - 45))
        elif (self.x, self.y - 45) not in plokid:  # Jätkan, kui plokke ees ei ole
            self.plahvatuskohad.append((self.x, self.y - 45))
            for i in range(self.pommitugevus-1):
                self.plahvatuskohad.append((self.x, self.y - (i+2)*45))
                if (self.x, self.y - (i+2)*45) in seinad:
                    seinad.remove((self.x, self.y - (i+2)*45))
                    if randint(1, 10) < 4:  # Boonuse loomine
                        loo_boonus(self.x, self.y - (i+2)*45)
                    break


class Boonus:
    def __init__(self, x, y, boonus):
        self.x = x
        self.y = y
        self.boonus = boonus
        self.algusaeg = time.time()
        self.olemas = True

    def uuenda(self):
        if time.time() - self.algusaeg > 10:
            self.olemas = False

def encode(data):
    data = json.dumps(data)
    data = data.encode()
    return data

def decode(data):
    data = data.decode()
    data = json.loads(data)
    return data

#def run():
running = True
clock = pygame.time.Clock()
playerN = 0

try:
    conn.sendto(encode("c"), (addr, serverport))
    while running:
        clock.tick(30)
        readable, writable, exceptional = (
            select.select(read_list, write_list, [], 0)
        )
        for f in readable:
            if f is conn:
                msg, addr = f.recvfrom(4048)
                ekraani_pind.blit(põrand, (0, 0))
                msg = decode(msg)
                cmd = msg[0]
                if cmd == "w":
                    plokid, seinad = msg[1], msg[2]
                    joonista_maailm(plokid, seinad)
                else:
                    if len(msg) > playerN:
                        for i in range(len(msg)-playerN):
                            print(i)
                            lisa_uus_mängija()
                        playerN = len(msg)
                        print(mängijad)
                    for i in range(len(msg)):
                        if msg[i][0] == "sinine":
                            x = 0
                        else:
                            x = 1
                        if msg[x][1] == "u":
                            mängijad[i].suundY = "up"
                        elif msg[x][1] == "d":
                            mängijad[i].suundY = "down"
                        elif msg[x][1] == "r":
                            mängijad[i].suundX = "right"
                        elif msg[x][1] == "l":
                            mängijad[i].suundX = "left"
                        elif msg[x][1] == "":
                            mängijad[x].suundX = ""
                            mängijad[x].suundY = ""
                        elif msg[x][1] == "b":
                            mängijad[x].aseta_pomm()

        ekraani_pind.blit(põrand, (0, 0))  # Joonistan põranda

        addr = "127.0.0.1"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:  # Klaviatuuri nuppude vajutamine

                if event.key == pygame.K_UP:
                    #mängijad[0].suundY = "up"
                    conn.sendto(encode("uu"), (addr, serverport))
                elif event.key == pygame.K_DOWN:
                    #mängijad[0].suundY = "down"
                    conn.sendto(encode("ud"), (addr, serverport))
                elif event.key == pygame.K_RIGHT:
                    #mängijad[0].suundX = "right"
                    conn.sendto(encode("ur"), (addr, serverport))
                elif event.key == pygame.K_LEFT:
                    #mängijad[0].suundX = "left"
                    conn.sendto(encode("ul"), (addr, serverport))
                pygame.event.clear(pygame.locals.KEYDOWN)

                if event.key == pygame.K_SPACE:
                    conn.sendto(encode("ub"), (addr, serverport))

            if event.type == pygame.KEYUP:  # Klaviatuuri nuppude lahtilaskmine

                if event.key == pygame.K_UP:
                    conn.sendto(encode("u"), (addr, serverport))
                elif event.key == pygame.K_DOWN:
                    conn.sendto(encode("u"), (addr, serverport))
                elif event.key == pygame.K_RIGHT:
                    conn.sendto(encode("u"), (addr, serverport))
                elif event.key == pygame.K_LEFT:
                    conn.sendto(encode("u"), (addr, serverport))

        for mängija in mängijad:
            mängija.uuenda()

        joonista_maailm(plokid, seinad)
        clock.tick(30)
        pygame.display.flip()
finally:
  addr = "127.0.0.1"
  conn.sendto(encode("d"), (addr, serverport))

#if __name__ == "__main__":
#  run()

"""running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:  # Klaviatuuri nuppude vajutamine

            if event.key == pygame.K_UP:
                if mängijad[0].suundY == "down":
                    mängijad[0].kahevahelY = True
                    mängijad[0].suundY = ""
                elif mängijad[0].suundX != "":
                    mängijad[0].suundY = "up"
                    mängijad[0].suundX = ""
                else:
                    mängijad[0].suundY = "up"

            elif event.key == pygame.K_DOWN:
                if mängijad[0].suundY == "up":
                    mängijad[0].kahevahelY = True
                    mängijad[0].suundY = ""
                elif mängijad[0].suundX != "":
                    mängijad[0].suundY = "down"
                    mängijad[0].suundX = ""
                else:
                    mängijad[0].suundY = "down"

            elif event.key == pygame.K_RIGHT:
                if mängijad[0].suundX == "left":
                    mängijad[0].kahevahelX = True
                    mängijad[0].suundX = ""
                elif mängijad[0].suundY != "":
                    mängijad[0].suundX = "right"
                    mängijad[0].suundY = ""
                else:
                    mängijad[0].suundX = "right"

            elif event.key == pygame.K_LEFT:
                if mängijad[0].suundX == "right":
                    mängijad[0].kahevahelX = True
                    mängijad[0].suundX = ""
                elif mängijad[0].suundY != "":
                    mängijad[0].suundX = "left"
                    mängijad[0].suundY = ""
                else:
                    mängijad[0].suundX = "left"
            if event.key == pygame.K_SPACE:
                mängijad[0].aseta_pomm()

        if event.type == pygame.KEYUP:  # Klaviatuuri nuppude lahtilaskmine

            if event.key == pygame.K_UP:
                if mängijad[0].kahevahelY:
                    mängijad[0].suundY = "down"
                    mängijad[0].kahevahelY = False
                else:
                    mängijad[0].suundY = ""
            elif event.key == pygame.K_DOWN:
                if mängijad[0].kahevahelY:
                    mängijad[0].suundY = "up"
                    mängijad[0].kahevahelY = False
                else:
                    mängijad[0].suundY = ""
            elif event.key == pygame.K_RIGHT:
                if mängijad[0].kahevahelX:
                    mängijad[0].suundX = "left"
                    mängijad[0].kahevahelX = False
                else:
                    mängijad[0].suundX = ""
            elif event.key == pygame.K_LEFT:
                if mängijad[0].kahevahelX:
                    mängijad[0].suundX = "right"
                    mängijad[0].kahevahelX = False
                else:
                    mängijad[0].suundX = ""

    ekraani_pind.fill((0, 0, 0))  # Puhastan ekraani

    ekraani_pind.blit(põrand, (0, 0))  # Joonistan põranda
    for mängija in mängijad:
        mängija.uuenda()

    for plokkXY in plokid:  # Joonistan plokid
        ekraani_pind.blit(plokk, plokkXY)
    for seinXY in seinad:  # Joonistan seinad
        ekraani_pind.blit(sein, seinXY)

    clock.tick(30)
    pygame.display.flip()  # Loon uue pildi"""
    

pygame.quit()
