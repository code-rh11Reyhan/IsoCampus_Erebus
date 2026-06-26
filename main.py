import pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 8
TILE_WIDTH = 64
TILE_HEIGHT = 32
ORIGIN_X = SCREEN_WIDTH // 2
ORIGIN_Y = 100
CUBE_HEIGHT = 20
running = True

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Isometrics')
clock = pygame.time.Clock()

# --- CAMERA ---
camera_x = 0.0
camera_y = 0.0
CAMERA_SPEED = 4.0
zoom = 1.0
ZOOM_SPEED = 0.05
MIN_ZOOM = 0.4
MAX_ZOOM = 2.5


def iso_to_screen(x, y):
    # World → isometric screen (pre-zoom, pre-camera)
    screen_x = ORIGIN_X + (x - y) * (TILE_WIDTH // 2)
    screen_y = ORIGIN_Y + (x + y) * (TILE_HEIGHT // 2)
    return screen_x, screen_y


def world_to_view(wx, wy):
    # Apply camera offset + zoom around screen centre
    sx, sy = iso_to_screen(wx, wy)
    vx = (sx - camera_x - SCREEN_WIDTH  // 2) * zoom + SCREEN_WIDTH  // 2
    vy = (sy - camera_y - SCREEN_HEIGHT // 2) * zoom + SCREEN_HEIGHT // 2
    return vx, vy


def draw_tile(surface, x, y, color, h=CUBE_HEIGHT):
    sx, sy = world_to_view(x, y)

    tw = (TILE_WIDTH  // 2) * zoom
    th = (TILE_HEIGHT // 2) * zoom
    ch =  h * zoom

    top = [
        (sx,      sy),
        (sx + tw, sy + th),
        (sx,      sy + th * 2),
        (sx - tw, sy + th),
    ]
    bottom = [(px, py + ch) for px, py in top]

    left  = [top[3], top[2], bottom[2], bottom[3]]
    right = [top[1], top[2], bottom[2], bottom[1]]

    pygame.draw.polygon(surface, (90,  90,  90),  left)
    pygame.draw.polygon(surface, (120, 120, 120), right)
    pygame.draw.polygon(surface, color,           top)
    pygame.draw.polygon(surface, (30,  30,  30),  left,  1)
    pygame.draw.polygon(surface, (30,  30,  30),  right, 1)
    pygame.draw.polygon(surface, (30,  30,  30),  top,   1)


while running:
    dt = clock.tick(60)
    screen.fill((20, 20, 30))

    keys = pygame.key.get_pressed()

    # WASD / arrow key camera pan (in world-iso space, not screen space)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        camera_y -= CAMERA_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        camera_y += CAMERA_SPEED
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        camera_x -= CAMERA_SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        camera_x += CAMERA_SPEED

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            zoom += event.y * ZOOM_SPEED
            zoom  = max(MIN_ZOOM, min(MAX_ZOOM, zoom))

    for gx in range(GRID_SIZE):
        for gy in range(GRID_SIZE):
            shade = 180 if (gx + gy) % 2 == 0 else 150
            draw_tile(screen, gx, gy, (shade, shade - 30, shade + 20))

    pygame.display.flip()

pygame.quit()
quit()