
import pygame
from constants import *


class Menu:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.font_big, self.font_med, self.font_small = fonts

        self.mode = None
        self.difficulty = 'MEDIUM'
        self.result = None

        self.frame = 0

        self.mode_buttons = [
            {'label': '2 PLAYERS', 'value': 'PVP',
             'rect': pygame.Rect(SCREEN_WIDTH // 2 - 240, 280, 210, 60)},
            {'label': 'VS COMPUTER', 'value': 'PVE',
             'rect': pygame.Rect(SCREEN_WIDTH // 2 + 30, 280, 210, 60)},
        ]
        self.diff_buttons = [
            {'label': 'EASY',   'value': 'EASY',
             'rect': pygame.Rect(SCREEN_WIDTH // 2 - 190, 380, 110, 50)},
            {'label': 'MEDIUM', 'value': 'MEDIUM',
             'rect': pygame.Rect(SCREEN_WIDTH // 2 - 55, 380, 110, 50)},
            {'label': 'HARD',   'value': 'HARD',
             'rect': pygame.Rect(SCREEN_WIDTH // 2 + 80, 380, 110, 50)},
        ]
        self.start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 470, 280, 65)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for btn in self.mode_buttons:
                if btn['rect'].collidepoint(mx, my):
                    self.mode = btn['value']

            if self.mode == 'PVE':
                for btn in self.diff_buttons:
                    if btn['rect'].collidepoint(mx, my):
                        self.difficulty = btn['value']

            if self.mode and self.start_rect.collidepoint(mx, my):
                self.result = (self.mode, self.difficulty)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.mode = 'PVP'
            elif event.key == pygame.K_2:
                self.mode = 'PVE'
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.mode:
                    self.result = (self.mode, self.difficulty)
            elif event.key == pygame.K_e and self.mode == 'PVE':
                self.difficulty = 'EASY'
            elif event.key == pygame.K_m and self.mode == 'PVE':
                self.difficulty = 'MEDIUM'
            elif event.key == pygame.K_h and self.mode == 'PVE':
                self.difficulty = 'HARD'

    def draw(self):
        self.frame += 1
        self.screen.fill(DARK_BG)

        # Animated grid background
        for gx in range(0, SCREEN_WIDTH + 1, 60):
            pygame.draw.line(self.screen, (25, 10, 55), (gx, 0), (gx, SCREEN_HEIGHT))
        for gy in range(0, SCREEN_HEIGHT + 1, 60):
            pygame.draw.line(self.screen, (25, 10, 55), (0, gy), (SCREEN_WIDTH, gy))

        # Title with pulsing glow
        pulse = abs(pygame.math.Vector2(1, 0).rotate(self.frame * 2).x)
        glow_r = int(80 + 60 * pulse)
        title_color = (255, glow_r, 200)
        title = self.font_big.render('STREET BRAWLER', True, title_color)
        tx = SCREEN_WIDTH // 2 - title.get_width() // 2
        shadow = self.font_big.render('STREET BRAWLER', True, (80, 0, 60))
        self.screen.blit(shadow, (tx + 4, 84))
        self.screen.blit(title, (tx, 80))

        sub = self.font_small.render('INSERT COIN TO PLAY', True, NEON_CYAN)
        sx = SCREEN_WIDTH // 2 - sub.get_width() // 2
        self.screen.blit(sub, (sx, 175))

        # Mode label
        ml = self.font_small.render('SELECT MODE', True, WHITE)
        self.screen.blit(ml, (SCREEN_WIDTH // 2 - ml.get_width() // 2, 240))

        # Mode buttons
        for btn in self.mode_buttons:
            selected = self.mode == btn['value']
            color = NEON_PINK if btn['value'] == 'PVP' else NEON_CYAN
            bg = (*color, 60) if selected else (20, 20, 40, 200)
            border_col = color if selected else (80, 80, 120)
            s = pygame.Surface(btn['rect'].size, pygame.SRCALPHA)
            s.fill(bg)
            self.screen.blit(s, btn['rect'].topleft)
            pygame.draw.rect(self.screen, border_col, btn['rect'], 2, border_radius=6)
            lbl = self.font_small.render(btn['label'], True, color if selected else LIGHT_GRAY)
            lx = btn['rect'].x + btn['rect'].w // 2 - lbl.get_width() // 2
            ly = btn['rect'].y + btn['rect'].h // 2 - lbl.get_height() // 2
            self.screen.blit(lbl, (lx, ly))

        # Difficulty selector (only when PVE)
        if self.mode == 'PVE':
            dl = self.font_small.render('DIFFICULTY', True, WHITE)
            self.screen.blit(dl, (SCREEN_WIDTH // 2 - dl.get_width() // 2, 345))

            diff_colors = {'EASY': GREEN, 'MEDIUM': YELLOW, 'HARD': RED}
            for btn in self.diff_buttons:
                selected = self.difficulty == btn['value']
                color = diff_colors[btn['value']]
                s = pygame.Surface(btn['rect'].size, pygame.SRCALPHA)
                bg_a = (*color, 80) if selected else (20, 20, 40, 200)
                s.fill(bg_a)
                self.screen.blit(s, btn['rect'].topleft)
                border_col = color if selected else (80, 80, 120)
                pygame.draw.rect(self.screen, border_col, btn['rect'], 2, border_radius=5)
                lbl = self.font_small.render(btn['label'], True, color if selected else LIGHT_GRAY)
                lx = btn['rect'].x + btn['rect'].w // 2 - lbl.get_width() // 2
                ly = btn['rect'].y + btn['rect'].h // 2 - lbl.get_height() // 2
                self.screen.blit(lbl, (lx, ly))

        # Start button
        can_start = self.mode is not None
        s_bg_col = (100, 0, 80, 180) if can_start else (30, 30, 50, 150)
        s = pygame.Surface(self.start_rect.size, pygame.SRCALPHA)
        s.fill(s_bg_col)
        self.screen.blit(s, self.start_rect.topleft)
        border = NEON_PINK if can_start else GRAY
        pygame.draw.rect(self.screen, border, self.start_rect, 2, border_radius=8)
        start_lbl = self.font_med.render('FIGHT!', True, NEON_PINK if can_start else GRAY)
        lx = self.start_rect.x + self.start_rect.w // 2 - start_lbl.get_width() // 2
        ly = self.start_rect.y + self.start_rect.h // 2 - start_lbl.get_height() // 2
        self.screen.blit(start_lbl, (lx, ly))

        # Controls hint
        y_c = 560
        hints = [
            ('P1: WASD=move  F=light  G=heavy  H=kick  SPACE=special', NEON_PINK),
        ]
        if self.mode == 'PVP':
            hints.append(('P2: Arrows=move  L/;/\'=attacks  ENTER=special', NEON_CYAN))
        elif self.mode == 'PVE':
            hints.append(('Press 1=PvP  2=VS COM  E/M/H=difficulty', LIGHT_GRAY))

        for text, color in hints:
            surf = pygame.font.SysFont('monospace', 13).render(text, True, color)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y_c))
            y_c += 22
