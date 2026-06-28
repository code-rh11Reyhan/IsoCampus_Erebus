import math
import pygame
import numpy as np

pygame.init()


TILES = [
    {"name": "grass",       "image": "images/grass.png",      "map_file": "maps/grass_map.txt"},
    {"name": "dirt_grass",  "image": "images/grass2.png",      "map_file": "maps/dirt_grass.txt"},
    {"name": "track_grass", "image": "images/track_grass.png", "map_file": "maps/track_grass.txt"},
    {"name": "cement",      "image": "images/cement.png",      "map_file": "maps/cement_map.txt"},
    {"name": "tree",        "image": "images/tree2.png",       "map_file": "maps/tree_map.txt"},
]

MARGIN = 20

REAL_TILE_W, REAL_TILE_H = 20, 24

EDITOR_SCALE = 2

SPRITE_W = REAL_TILE_W * EDITOR_SCALE
SPRITE_H = REAL_TILE_H * EDITOR_SCALE

TILE_W = SPRITE_W
TILE_H = TILE_W / 2
HW, HH = TILE_W / 2, TILE_H / 2

PALETTE_CELL = 28
PALETTE_ITEM_H = PALETTE_CELL + 28
PALETTE_W = 140

status_msg   = ""
status_timer = 0          
STATUS_DURATION = 120     

WINDOW_W = 1024
WINDOW_H = 680

for tile in TILES:
    with open(tile["map_file"]) as f:
        rows = [r for r in f.read().splitlines() if r]
    tile["data"] = [[int(c) for c in row] for row in rows]

GRID_ROWS = len(TILES[0]["data"])
GRID_COLS = len(TILES[0]["data"][0])

for tile in TILES:
    h, w = len(tile["data"]), len(tile["data"][0])
    assert h == GRID_ROWS and w == GRID_COLS, (
        f"{tile['name']} map is {w}x{h}, expected {GRID_COLS}x{GRID_ROWS}"
    )

M = np.array([[HW, -HW],
              [HH,  HH]])
M_INV = np.linalg.inv(M)


ORIGIN_Y = MARGIN
ORIGIN_X = MARGIN   

def recalc_origin():
    global ORIGIN_X
    ORIGIN_X = MARGIN + (GRID_ROWS - 1) * HW

recalc_origin()   


VIEWPORT_W = WINDOW_W - PALETTE_W - MARGIN * 2


_grid_pixel_w = HW * (GRID_COLS + GRID_ROWS - 1)
cam_x = (VIEWPORT_W - _grid_pixel_w) / 2 - ORIGIN_X + MARGIN
cam_y = 0.0

panning      = False
pan_start_mouse  = (0, 0)
pan_start_cam    = (0.0, 0.0)

palette_origin = (WINDOW_W - PALETTE_W - MARGIN, MARGIN)

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("IsoCampus-Erebus - Level Editor")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 14)

for tile in TILES:
    img = pygame.image.load(tile["image"]).convert()
    img.set_colorkey((0, 0, 0))
    tile["image_obj"] = pygame.transform.scale(img, (SPRITE_W, SPRITE_H))

selected_index = 0




def save_maps():
    """Write every tile's data back to its .txt file, row by row."""
    for tile in TILES:
        with open(tile["map_file"], "w") as f:
            for row in tile["data"]:
                f.write("".join(str(v) for v in row) + "\n")


def load_maps():
    """Re-read every tile's .txt file from disk into memory."""
    for tile in TILES:
        with open(tile["map_file"]) as f:
            rows = [r for r in f.read().splitlines() if r]
        tile["data"] = [[int(c) for c in row] for row in rows]




EXTEND_AMOUNT = 5

def extend_plus_x():
    """Append 5 empty columns to the right of every row."""
    global GRID_COLS
    for tile in TILES:
        for row in tile["data"]:
            row += [0] * EXTEND_AMOUNT
    GRID_COLS += EXTEND_AMOUNT

def extend_minus_x():
    """Prepend 5 empty columns to the left of every row.
    Shifts ORIGIN_X right so existing content stays in place on screen."""
    global GRID_COLS, cam_x
    for tile in TILES:
        for row in tile["data"]:
            row[:0] = [0] * EXTEND_AMOUNT   
    GRID_COLS += EXTEND_AMOUNT
    
    cam_x -= EXTEND_AMOUNT * HW

def extend_plus_y():
    """Append 5 empty rows to the bottom of the grid."""
    global GRID_ROWS
    for tile in TILES:
        tile["data"] += [[0] * GRID_COLS for _ in range(EXTEND_AMOUNT)]
    GRID_ROWS += EXTEND_AMOUNT
    recalc_origin()   

def extend_minus_y():
    """Prepend 5 empty rows to the top of the grid.
    Shifts ORIGIN_X right (more rows = bigger left-tip padding) and adjusts cam_x."""
    global GRID_ROWS, cam_x
    new_rows = [[0] * GRID_COLS for _ in range(EXTEND_AMOUNT)]
    for tile in TILES:
        tile["data"][:0] = [list(r) for r in new_rows]
    old_origin_x = ORIGIN_X
    GRID_ROWS += EXTEND_AMOUNT
    recalc_origin()
    
    cam_x -= (ORIGIN_X - old_origin_x)



def grid_to_screen(gx, gy):
    """Iso grid cell → screen pixel (top-left of the sprite blit rect)."""
    sx, sy = M @ np.array([gx, gy])
    return ORIGIN_X + cam_x + sx, ORIGIN_Y + cam_y + sy


def screen_to_grid(mx, my):
    """Screen pixel → (gx, gy) grid cell (floored)."""
    sx = mx - ORIGIN_X - cam_x
    sy = my - ORIGIN_Y - cam_y
    x, y = M_INV @ np.array([sx, sy])
    return math.floor(x), math.floor(y)



def draw_grid():
    vp_rect = pygame.Rect(0, 0, VIEWPORT_W + MARGIN * 2, WINDOW_H)

    for gy in range(GRID_ROWS):
        for gx in range(GRID_COLS):
            sx, sy = grid_to_screen(gx, gy)

            if sx + HW < 0 or sx - HW > vp_rect.right:
                continue
            if sy + SPRITE_H < 0 or sy > WINDOW_H:
                continue

            top    = (sx,      sy)
            right  = (sx + HW, sy + HH)
            bottom = (sx,      sy + TILE_H)
            left   = (sx - HW, sy + HH)
            pygame.draw.polygon(screen, (60, 60, 65), [top, right, bottom, left], 1)

            for tile in TILES:
                if tile["data"][gy][gx]:
                    screen.blit(tile["image_obj"], (sx - HW, sy))


def draw_palette():
    ox, oy = palette_origin
    icon_h = PALETTE_CELL
    icon_w = round(icon_h * REAL_TILE_W / REAL_TILE_H)
    for i, tile in enumerate(TILES):
        rect = pygame.Rect(ox, oy + i * PALETTE_ITEM_H, PALETTE_CELL + 10, PALETTE_CELL + 10)
        is_selected = (i == selected_index)
        pygame.draw.rect(screen, (90, 90, 40) if is_selected else (45, 45, 50), rect)
        swatch = pygame.transform.scale(tile["image_obj"], (icon_w, icon_h))
        screen.blit(swatch, (rect.centerx - icon_w // 2, rect.y + 5))
        label = font.render(tile["name"], True, (230, 230, 230))
        screen.blit(label, (rect.x, rect.bottom + 2))
        if is_selected:
            pygame.draw.rect(screen, (255, 210, 60), rect, 2)


def palette_index_at_mouse(pos):
    ox, oy = palette_origin
    for i in range(len(TILES)):
        rect = pygame.Rect(ox, oy + i * PALETTE_ITEM_H, PALETTE_CELL + 10, PALETTE_CELL + 10)
        if rect.collidepoint(pos):
            return i
    return None




def _all_btn_rects():
    """Return a dict of action -> pygame.Rect, computed fresh each call."""
    ox  = palette_origin[0]
    bw  = PALETTE_W - MARGIN        # button width
    bh  = 24                        # button height
    gap = 4                         # gap between buttons
    sec = 10                        # larger gap between sections

    bottom = WINDOW_H - MARGIN

    load_rect     = pygame.Rect(ox, bottom - bh,                                   bw, bh)
    save_rect     = pygame.Rect(ox, bottom - bh * 2 - gap,                         bw, bh)
    ext_my_rect   = pygame.Rect(ox, bottom - bh * 3 - gap - sec,                   bw, bh)
    ext_py_rect   = pygame.Rect(ox, bottom - bh * 4 - gap * 2 - sec,               bw, bh)
    ext_mx_rect   = pygame.Rect(ox, bottom - bh * 5 - gap * 3 - sec,               bw, bh)
    ext_px_rect   = pygame.Rect(ox, bottom - bh * 6 - gap * 4 - sec,               bw, bh)

    return {
        "load":      load_rect,
        "save":      save_rect,
        "extend_-y": ext_my_rect,
        "extend_+y": ext_py_rect,
        "extend_-x": ext_mx_rect,
        "extend_+x": ext_px_rect,
    }


def draw_buttons():
    rects = _all_btn_rects()
    specs = [
        ("save",      "SAVE",      (50, 120,  60)),
        ("load",      "LOAD",      (50,  80, 130)),
        ("extend_+x", "+X  (+5 col right)",  (100,  70,  70)),
        ("extend_-x", "-X  (+5 col left)",   (100,  70,  70)),
        ("extend_+y", "+Y  (+5 row bottom)", ( 70,  70, 110)),
        ("extend_-y", "-Y  (+5 row top)",    ( 70,  70, 110)),
    ]
    small_font = pygame.font.SysFont("consolas", 11)
    for key, label, colour in specs:
        rect = rects[key]
        pygame.draw.rect(screen, colour, rect, border_radius=4)
        pygame.draw.rect(screen, (160, 160, 160), rect, 1, border_radius=4)
        f = font if len(label) <= 6 else small_font
        txt = f.render(label, True, (230, 230, 230))
        screen.blit(txt, txt.get_rect(center=rect.center))

    lbl = pygame.font.SysFont("consolas", 11).render("── extend grid ──", True, (110, 110, 110))
    top_btn = rects["extend_+x"]
    screen.blit(lbl, (top_btn.x, top_btn.y - 14))


def button_hit(pos):
    """Return an action string or None."""
    for action, rect in _all_btn_rects().items():
        if rect.collidepoint(pos):
            return action
    return None




running = True
while running:
    screen.fill((20, 20, 24))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            panning = True
            pan_start_mouse = event.pos
            pan_start_cam   = (cam_x, cam_y)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            panning = False

        elif event.type == pygame.MOUSEMOTION:
            if panning:
                dx = event.pos[0] - pan_start_mouse[0]
                dy = event.pos[1] - pan_start_mouse[1]
                cam_x = pan_start_cam[0] + dx
                cam_y = pan_start_cam[1] + dy

        elif event.type == pygame.MOUSEBUTTONDOWN:
            action = button_hit(event.pos)
            if action == "save":
                save_maps()
                status_msg   = "Saved!"
                status_timer = STATUS_DURATION
                continue
            if action == "load":
                load_maps()
                status_msg   = "Loaded!"
                status_timer = STATUS_DURATION
                continue
            if action == "extend_+x":
                extend_plus_x()
                status_msg   = f"Grid now {GRID_COLS}x{GRID_ROWS}"
                status_timer = STATUS_DURATION
                continue
            if action == "extend_-x":
                extend_minus_x()
                status_msg   = f"Grid now {GRID_COLS}x{GRID_ROWS}"
                status_timer = STATUS_DURATION
                continue
            if action == "extend_+y":
                extend_plus_y()
                status_msg   = f"Grid now {GRID_COLS}x{GRID_ROWS}"
                status_timer = STATUS_DURATION
                continue
            if action == "extend_-y":
                extend_minus_y()
                status_msg   = f"Grid now {GRID_COLS}x{GRID_ROWS}"
                status_timer = STATUS_DURATION
                continue

            pal_idx = palette_index_at_mouse(event.pos)
            if pal_idx is not None:
                selected_index = pal_idx
                continue

            if event.pos[0] > VIEWPORT_W + MARGIN * 2:
                continue

            gx, gy = screen_to_grid(*event.pos)
            if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                if event.button == 1:
                    TILES[selected_index]["data"][gy][gx] = 1
                elif event.button == 3:
                    for tile in TILES:
                        tile["data"][gy][gx] = 0

    draw_grid()
    draw_palette()
    draw_buttons()

    sep_x = VIEWPORT_W + MARGIN * 2
    pygame.draw.line(screen, (50, 50, 55), (sep_x, 0), (sep_x, WINDOW_H))

    hint = font.render(
        "Left: paint   Right: erase   Middle-drag: pan",
        True, (160, 160, 160)
    )
    screen.blit(hint, (MARGIN, WINDOW_H - 20))

    if status_timer > 0:
        if status_msg == "Saved!":
            colour = (100, 220, 120)
        elif status_msg == "Loaded!":
            colour = (100, 160, 220)
        else:
            colour = (220, 180, 100)   
        msg_surf = font.render(status_msg, True, colour)
        ox, _ = palette_origin
        screen.blit(msg_surf, (ox, WINDOW_H - 80))
        status_timer -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()