import pygame


pygame.init()

pygame.display.set_caption("IsoCampus-Erebus")
screen = pygame.display.set_mode((800, 800))
display  = pygame.Surface((300, 300))

# All Images Are Gonna Be Mentioned Here Only

grass_img = pygame.image.load('images/grass.png').convert()
tree_img = pygame.image.load('images/tree2.png').convert()
track_grass = pygame.image.load('images/track_grass.png').convert()



# Setting every color key at once
grass_img.set_colorkey((0, 0, 0))
tree_img.set_colorkey((0, 0, 0))
track_grass.set_colorkey((0, 0, 0))



f = open('maps/grass_map.txt')
grass_data = [[int(c) for c in row] for row in f.read().split('\n')]
f.close()

f = open('maps/tree_map.txt')
tree_data = [[int(c) for c in row] for row in f.read().split('\n')]
f.close()

f = open('maps/track_grass.txt')
track_grass_data = [[int(c) for c in row] for row in f.read().split('\n')]
f.close()

# Game Variables
running = True
camera_x = 150
camera_y = 100
camera_speed = 2
clock = pygame.time.Clock()






while running:

    display.fill((30, 30, 30))

    for y, row in enumerate(grass_data):
        for x, tile in enumerate(row):
            if tile:
                pygame.draw.rect(display, (255, 255, 255), pygame.Rect(x*2, y*2, 3, 3), 1)
                display.blit(grass_img, (camera_x + x*10 - y*10, camera_y+ x*5+ y*5+14))
                display.blit(grass_img, (camera_x+ x*10 - y*10, camera_y+ x*5+ y*5))
                
            if tree_data[y][x]:
                display.blit(tree_img, (camera_x + x*10- y*10, camera_y + x*5+ y*5 - 16))
            if track_grass_data[y][x]:
                display.blit(track_grass, (camera_x + x*10- y*10, camera_y + x*5+ y*5 - 16))
                
            

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



