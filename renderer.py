
import pygame
from constants import *


def draw_stage(screen):
    screen.fill(DARK_BG)

    # Sky gradient effect
    for i in range(200):
        frac = i / 200
        r = int(8 + frac * 20)
        g = int(8 + frac * 10)
        b = int(18 + frac * 50)
        pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

    # Back buildings silhouette
    buildings_back = [
        (0, 260, 80, 180),
        (90, 300, 60, 140),
        (160, 230, 100, 210),
        (270, 290, 70, 160),
        (350, 240, 120, 200),
        (480, 310, 55, 140),
        (540, 260, 90, 190),
        (640, 320, 65, 130),
        (710, 270, 100, 180),
        (820, 250, 80, 200),
        (910, 300, 70, 150),
        (990, 260, 90, 190),
        (1090, 290, 110, 160),
    ]
    for bx, by, bw, bh in buildings_back:
        color = (18, 16, 38)
        pygame.draw.rect(screen, color, (bx, by, bw, bh))
        # Windows
        for wy in range(by + 10, by + bh - 10, 20):
            for wx in range(bx + 8, bx + bw - 8, 15):
                lit = (wx + wy) % 37 != 0
                wcol = (60, 55, 20) if lit else (20, 18, 35)
                pygame.draw.rect(screen, wcol, (wx, wy, 7, 10))

    # Midground
    buildings_mid = [
        (50, 340, 70, 100),
        (130, 360, 50, 90),
        (190, 320, 80, 130),
        (280, 350, 60, 100),
        (360, 330, 90, 120),
        (460, 355, 50, 95),
        (520, 325, 75, 125),
        (610, 350, 65, 100),
        (690, 335, 80, 115),
        (790, 345, 55, 105),
        (860, 320, 85, 130),
        (960, 350, 60, 100),
        (1040, 330, 80, 120),
        (1130, 355, 70, 95),
    ]
    for bx, by, bw, bh in buildings_mid:
        color = (24, 20, 50)
        pygame.draw.rect(screen, color, (bx, by, bw, bh))

    # Neon ground grid lines
    grid_color = (40, 20, 80)
    for gx in range(0, SCREEN_WIDTH + 1, 60):
        pygame.draw.line(screen, grid_color, (gx, GROUND_Y), (gx, SCREEN_HEIGHT))
    pygame.draw.line(screen, (60, 30, 120), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)

    # Floor
    pygame.draw.rect(screen, STAGE_COLOR, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    pygame.draw.rect(screen, (50, 40, 90), (0, GROUND_Y, SCREEN_WIDTH, 3))

    # Neon floor grid perspective
    for gx in range(0, SCREEN_WIDTH + 1, 80):
        ratio = gx / SCREEN_WIDTH
        end_x = int(SCREEN_WIDTH / 2 + (gx - SCREEN_WIDTH / 2) * 0.2)
        col_intensity = int(30 + 40 * (1 - abs(ratio - 0.5) * 2))
        pygame.draw.line(screen, (col_intensity, 10, col_intensity * 2),
                         (gx, GROUND_Y), (end_x, SCREEN_HEIGHT), 1)


def draw_hud(screen, fighters, round_timer, round_number, fonts):
    font_big, font_med, font_small = fonts

    bar_w = 420
    bar_h = 26
    bar_border = 3
    padding = 20
    p1 = fighters[0]
    p2 = fighters[1]

    # P1 health bar (left-aligned, fills right)
    p1_ratio = max(0, p1.health / p1.maxHealth) if hasattr(p1, 'maxHealth') else max(0, p1.health / MAX_HEALTH)
    p1_fill = int(bar_w * p1_ratio)
    p1_color = _health_color(p1_ratio)

    p1_bar_rect = pygame.Rect(padding, padding, bar_w, bar_h)
    pygame.draw.rect(screen, DARK_GRAY, p1_bar_rect, border_radius=4)
    if p1_fill > 0:
        pygame.draw.rect(screen, p1_color, (padding, padding, p1_fill, bar_h), border_radius=4)
    pygame.draw.rect(screen, WHITE, p1_bar_rect, bar_border, border_radius=4)

    # P1 name
    p1_name = font_small.render(p1.name, True, NEON_PINK)
    screen.blit(p1_name, (padding, padding + bar_h + 4))

    # P1 win dots
    _draw_wins(screen, p1.wins, padding, padding + bar_h + 22, 1)

    # P2 health bar (right-aligned, fills left)
    p2_ratio = max(0, p2.health / MAX_HEALTH)
    p2_fill = int(bar_w * p2_ratio)
    p2_color = _health_color(p2_ratio)
    p2_bar_x = SCREEN_WIDTH - padding - bar_w

    p2_bar_rect = pygame.Rect(p2_bar_x, padding, bar_w, bar_h)
    pygame.draw.rect(screen, DARK_GRAY, p2_bar_rect, border_radius=4)
    if p2_fill > 0:
        fill_x = p2_bar_x + bar_w - p2_fill
        pygame.draw.rect(screen, p2_color, (fill_x, padding, p2_fill, bar_h), border_radius=4)
    pygame.draw.rect(screen, WHITE, p2_bar_rect, bar_border, border_radius=4)

    # P2 name
    p2_name = font_small.render(p2.name, True, NEON_CYAN)
    screen.blit(p2_name, (SCREEN_WIDTH - padding - p2_name.get_width(), padding + bar_h + 4))

    # P2 win dots
    _draw_wins(screen, p2.wins, SCREEN_WIDTH - padding, padding + bar_h + 22, -1)

    # Timer
    secs = max(0, round_timer // FPS)
    timer_color = RED if secs <= 10 else WHITE
    timer_surf = font_big.render(str(secs), True, timer_color)
    tx = SCREEN_WIDTH // 2 - timer_surf.get_width() // 2
    screen.blit(timer_surf, (tx, padding - 2))

    # Round label
    round_surf = font_small.render(f'ROUND {round_number}', True, YELLOW)
    rx = SCREEN_WIDTH // 2 - round_surf.get_width() // 2
    screen.blit(round_surf, (rx, padding + bar_h + 4))


def draw_announcement(screen, text, font_big, alpha=255):
    if not text:
        return
    colors = {
        'FIGHT!': NEON_YELLOW,
        'KO!': NEON_PINK,
        'DRAW!': LIGHT_GRAY,
    }
    color = colors.get(text, NEON_CYAN)

    surf = font_big.render(text, True, color)
    x = SCREEN_WIDTH // 2 - surf.get_width() // 2
    y = SCREEN_HEIGHT // 2 - surf.get_height() // 2 - 40

    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    glow.blit(surf, (0, 0))

    screen.blit(surf, (x, y))

    outline = font_big.render(text, True, BLACK)
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        screen.blit(outline, (x + dx, y + dy))
    screen.blit(surf, (x, y))


def draw_hit_effect(screen, x, y, color):
    for i in range(6):
        angle = i * 60
        ex = int(x + 25 * pygame.math.Vector2(1, 0).rotate(angle).x)
        ey = int(y + 25 * pygame.math.Vector2(1, 0).rotate(angle).y)
        pygame.draw.line(screen, color, (int(x), int(y)), (ex, ey), 3)
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), 8)


def _health_color(ratio):
    if ratio > 0.5:
        return GREEN
    elif ratio > 0.25:
        return YELLOW
    else:
        return RED


def _draw_wins(screen, wins, x, y, direction):
    for i in range(MAX_ROUNDS // 2 + 1):
        filled = i < wins
        cx = x + direction * (i * 18 + 9)
        color = YELLOW if filled else DARK_GRAY
        pygame.draw.circle(screen, color, (cx, y), 7)
        pygame.draw.circle(screen, WHITE, (cx, y), 7, 1)
