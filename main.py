import pygame


pygame.init()

pygame.display.set_caption("IsoCampus-Erebus")
screen = pygame.display.set_mode((800, 800))
display  = pygame.Surface((300, 300))

# All Images Are Gonna Be Mentioned Here Only

grass_img = pygame.image.load('images/grass.png').convert()




# Setting every color key at once
grass_img.set_colorkey((0, 0, 0))




f = open('map.txt')

map_data = [[int(c) for c in row] for row in f.read().split('\n')]
f.close()


# Game Variables
running = True
camera_x = 150
camera_y = 100
camera_speed = 2
clock = pygame.time.Clock()






while running:

    display.fill((0, 0, 0))

    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile:
                pygame.draw.rect(display, (255, 255, 255), pygame.Rect(x*2, y*2, 3, 3), 1)
                display.blit(grass_img, (camera_x+ x*10 - y*10, camera_y+ x*5+ y*5))
                display.blit(grass_img, (camera_x + x*10 - y*10, camera_y+ x*5+ y*5-14))
                
                
            

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        camera_x -= camera_speed
    if keys[pygame.K_LEFT]:
        camera_x += camera_speed
    if keys[pygame.K_UP]:
        camera_y += camera_speed
    if keys[pygame.K_DOWN]:
        camera_y -= camera_speed
        

        
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.flip()
    clock.tick(60)
    
    

pygame.quit()
quit()



