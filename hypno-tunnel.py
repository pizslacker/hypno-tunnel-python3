#!/usr/bin/env python3
import pygame
import math
import time

SCREEN_W = 1280
SCREEN_H = 720

# Cube Dimensions
TILE_W = 48
TILE_H = 24
CUBE_Z = 24

# Color Palette (RGB) based on Amiga/ANSI colors
PALETTE = [
    (255, 50,  50),  # Red
    (50,  255, 50),  # Green
    (255, 200, 50),  # Yellow
    (50,  150, 255), # Blue
    (255, 50,  255), # Magenta
    (50,  255, 255)  # Cyan
]

def draw_iso_cube(surface, sx, sy, base_color):
    """Draws a 3D isometric cube using three shaded polygons."""
    # Shading modifiers (Top 100%, Left 70%, Right 40%)
    top_col = base_color
    left_col = (int(base_color[0] * 0.7), int(base_color[1] * 0.7), int(base_color[2] * 0.7))
    right_col = (int(base_color[0] * 0.4), int(base_color[1] * 0.4), int(base_color[2] * 0.4))

    hw = TILE_W / 2.0
    hh = TILE_H / 2.0
    z = CUBE_Z

    # Top face
    pygame.draw.polygon(surface, top_col, [
        (sx, sy), 
        (sx - hw, sy + hh), 
        (sx, sy + TILE_H), 
        (sx + hw, sy + hh)
    ])

    # Left face
    pygame.draw.polygon(surface, left_col, [
        (sx - hw, sy + hh), 
        (sx, sy + TILE_H), 
        (sx, sy + TILE_H + z), 
        (sx - hw, sy + hh + z)
    ])

    # Right face
    pygame.draw.polygon(surface, right_col, [
        (sx, sy + TILE_H), 
        (sx + hw, sy + hh), 
        (sx + hw, sy + hh + z), 
        (sx, sy + TILE_H + z)
    ])

def hash2d(x, y):
    """Pseudo-random hash for per-cube jitter."""
    # Python integers have arbitrary precision. We mask with 0xFFFFFFFF 
    # to emulate the 32-bit integer overflow behavior of the original C code.
    n = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return (n & 0x7FFFFFFF) / 0x7FFFFFFF

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Python Demoscene - Isometric Floor")
    clock = pygame.time.Clock()

    horizon_y = SCREEN_H // 3
    max_depth = int((SCREEN_H - horizon_y + 100) / (TILE_H / 2))
    cols_w = (SCREEN_W // TILE_W) + 4

    start_time = time.time()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        t = time.time() - start_time

        # Clear screen to deep retro purple/black
        screen.fill((20, 10, 30))

        # Render back-to-front (depth D) and left-to-right (column C)
        for d in range(max_depth):
            for c in range(-cols_w // 2, cols_w // 2 + 1):
                
                # Base screen coordinates
                sx = c * TILE_W + (SCREEN_W / 2.0)
                if d % 2 != 0:
                    sx += TILE_W / 2.0  # Stagger odd rows

                # Map to theoretical grid coordinates for math
                x = (d + c * 2.0) / 2.0
                y = (d - c * 2.0) / 2.0

                center_d = max_depth / 2.0
                dx = c * 2.0
                dy = d - center_d
                dist = math.sqrt(dx * dx + dy * dy)

                # Wave math (amplitudes scaled up for pixels)
                ripple = math.sin(dist * 0.15 - t * 4.0) * 40.0
                diag = math.sin((x + y) * 0.1 + t * 2.0) * 20.0
                
                # Per-cube jitter using the hash function
                grid_x, grid_y = int(x), int(y)
                rnd = (hash2d(grid_x, grid_y) - 0.5) * math.sin(t * 3.0 + hash2d(grid_x, grid_y) * 6.28) * 10.0

                h = ripple + diag + rnd
                sy = horizon_y + d * (TILE_H / 2.0) - h

                # Modulo cycling through our retro palette
                color_idx = (abs(grid_x) + abs(grid_y)) % 6

                # Render bounding check (Don't draw cubes completely off-screen)
                if -CUBE_Z < sy < SCREEN_H:
                    draw_iso_cube(screen, sx, sy, PALETTE[color_idx])

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()