import pygame

pygame.init()

ekraani_pind = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Best project in Turu 19 - 16")


xspeedC = 2 # Kuuli kiirus X-teljel
yspeedC = -2 # Kuuli kiirus Y-teljel
xposC = 320  # Kuuli positsioom X-teljel
yposC = 450  # Kuuli positsioon Y-teljel
raadiusC = 20 # Kuuli raadius

telliselaius = 60
tellisekõrgus = 30

tellised = [[100,0],[170,0],[240,0],[310,0],[380,0]]

pygame.display.flip() # Joonistab pildi

clock = pygame.time.Clock()

while True:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        break

    if xposC < 20 or xposC > 620: # Hoian kuuli raamides
        xspeedC *= -1
    if yposC < 20 or yposC > 460:
        yspeedC *= -1
        
    i = 0 # Indeks telliste listis telliste loendamiseks (et remove-ga järgnevat tellist vahele ei jätaks)
    while i < len(tellised): #  Telliste kaotamine <-------------------------------
        if yposC - raadiusC < tellised[i][1] + tellisekõrgus and yposC + raadiusC > tellised[i][1] and xposC - raadiusC < tellised[i][0] + telliselaius and xposC + raadiusC > tellised[i][0]:
            if yposC < tellised[i][1] and not yposC + (raadiusC + 1) > tellised[i][1]:
                yspeedC *= -1
            elif yposC > tellised[i][1] + tellisekõrgus and not yposC - (raadiusC + 1) < tellised[i][1]:
                yspeedC *= -1
            elif xposC < tellised[i][0] and not xposC + (raadiusC + 1) > tellised[i][0]:
                xspeedC *= -1
            else:
                xspeedC *= -1
            del tellised[i]
            i -= 1 # Võtan indeksilt ühe maha, et järgnevat tellist vahele ei jäetaks
        i += 1
    ekraani_pind.fill((0,0,0)) # Puhastan ekraani
    
    ekraani_pind.fill((230,240,250))
    
    xposC += xspeedC # Nihutan kuuli olenevalt kiirustest
    yposC += yspeedC
    
    pygame.draw.circle(ekraani_pind, (0,255,0), (xposC, yposC), raadiusC, 0) # Joonistan uue kuuli

    for i in range(len(tellised)):
        brick = pygame.Rect(tellised[i][0], tellised[i][1], telliselaius, tellisekõrgus)
        pygame.draw.rect(ekraani_pind, (250,55,55), brick)

    if len(tellised) == 0:
        break
    pygame.display.flip() # Loon uue ekraani
    clock.tick(300)  # Jooksutan kella
pygame.quit()
