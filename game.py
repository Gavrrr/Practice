
import pygame
from constants import *
from fighter import Fighter, Projectile
from ai import compute_ai
from renderer import draw_stage, draw_hud, draw_announcement, draw_hit_effect


def create_fighters():
    p1 = Fighter(0, 280, GROUND_Y - FIGHTER_HEIGHT, RED, (255, 255, 220), 'RYU', 1)
    p1.maxHealth = MAX_HEALTH
    p2 = Fighter(1, SCREEN_WIDTH - 280 - FIGHTER_WIDTH, GROUND_Y - FIGHTER_HEIGHT,
                 BLUE, GOLD, 'KEN', -1)
    p2.maxHealth = MAX_HEALTH
    return p1, p2


class Game:
    def __init__(self, mode, difficulty, screen, fonts):
        self.mode = mode
        self.difficulty = difficulty
        self.screen = screen
        self.fonts = fonts
        self.font_big, self.font_med, self.font_small = fonts

        self.p1, self.p2 = create_fighters()
        self.fighters = [self.p1, self.p2]

        self.projectiles = []
        self.hit_effects = []

        self.round_timer = ROUND_TIME * FPS
        self.round_number = 1

        self.match_state = 'FIGHTING'
        self.winner = None

        self.announcement = 'FIGHT!'
        self.announcement_timer = 90

        self.ai_last_action = {
            'up': False, 'down': False, 'left': False, 'right': False,
            'light': False, 'heavy': False, 'kick': False,
            'special': False, 'block': False
        }

        self.frame_count = 0
        self.result = None

    def get_state_dict(self):
        return {
            'fighters': self.fighters,
            'projectiles': self.projectiles,
            'match_state': self.match_state,
        }

    def _map_p1_keys(self, keys):
        return {
            'up':      keys[pygame.K_w],
            'down':    keys[pygame.K_s],
            'left':    keys[pygame.K_a],
            'right':   keys[pygame.K_d],
            'light':   keys[pygame.K_f],
            'heavy':   keys[pygame.K_g],
            'kick':    keys[pygame.K_h],
            'special': keys[pygame.K_SPACE],
            'block':   keys[pygame.K_s],
        }

    def _map_p2_keys(self, keys):
        return {
            'up':      keys[pygame.K_UP],
            'down':    keys[pygame.K_DOWN],
            'left':    keys[pygame.K_LEFT],
            'right':   keys[pygame.K_RIGHT],
            'light':   keys[pygame.K_KP1] or keys[pygame.K_l],
            'heavy':   keys[pygame.K_KP2] or keys[pygame.K_SEMICOLON],
            'kick':    keys[pygame.K_KP3] or keys[pygame.K_QUOTE],
            'special': keys[pygame.K_KP0] or keys[pygame.K_RETURN],
            'block':   keys[pygame.K_DOWN],
        }

    def update(self, keys):
        self.frame_count += 1

        if self.match_state != 'FIGHTING':
            if self.announcement_timer > 0:
                self.announcement_timer -= 1
            return

        if self.announcement_timer > 0:
            self.announcement_timer -= 1

        # Inputs
        p1_action = self._map_p1_keys(keys)

        if self.mode == 'PVE':
            p2_action = compute_ai(self.get_state_dict(), self.difficulty,
                                   self.ai_last_action, self.frame_count)
            self.ai_last_action = p2_action
        else:
            p2_action = self._map_p2_keys(keys)

        # Apply actions
        proj1 = self.p1.apply_action(p1_action)
        proj2 = self.p2.apply_action(p2_action)
        if proj1:
            self.projectiles.append(proj1)
        if proj2:
            self.projectiles.append(proj2)

        # Update fighters
        for f in self.fighters:
            f.update()

        # Face each other
        if self.p1.state not in ('hitstun', 'dead') and self.p2.state not in ('hitstun', 'dead'):
            self.p1.facing = 1 if self.p2.x > self.p1.x else -1
            self.p2.facing = 1 if self.p1.x > self.p2.x else -1

        # Keep fighters apart (push out)
        sep = self._separate_fighters()

        # Attack collisions (melee)
        self._check_melee()

        # Projectile updates and collisions
        self._update_projectiles()

        # Update hit effects
        self.hit_effects = [(x, y, c, t - 1) for x, y, c, t in self.hit_effects if t > 1]

        # Timer
        if self.round_timer > 0:
            self.round_timer -= 1
        else:
            self._end_round_by_timer()
            return

        # Check KO
        if self.p1.state == 'dead' or self.p2.state == 'dead':
            self._end_round_by_ko()

    def _separate_fighters(self):
        overlap = (self.p1.x + self.p1.width) - self.p2.x
        if overlap > 0 and self.p1.x < self.p2.x:
            push = overlap / 2
            self.p1.x -= push
            self.p2.x += push

    def _check_melee(self):
        for attacker, defender in [(self.p1, self.p2), (self.p2, self.p1)]:
            if not attacker.is_attacking():
                continue
            if attacker.has_hit:
                continue
            hb = attacker.get_attack_hitbox()
            if hb and hb.colliderect(defender.get_rect()):
                attacker.has_hit = True
                dmg_map = {
                    'attack_light': LIGHT_DMG,
                    'attack_heavy': HEAVY_DMG,
                    'attack_kick':  KICK_DMG,
                }
                dmg = dmg_map.get(attacker.state, LIGHT_DMG)
                kdir = 1 if attacker.x < defender.x else -1
                defender.take_hit(dmg, kdir)
                hx = defender.x + defender.width // 2
                hy = defender.y + defender.height // 2
                self.hit_effects.append((hx, hy, attacker.secondary_color, 12))

    def _update_projectiles(self):
        to_remove = []
        for proj in self.projectiles:
            proj.update()
            if not proj.active:
                to_remove.append(proj)
                continue
            for fighter in self.fighters:
                if fighter.id == proj.owner_id:
                    continue
                if proj.get_rect().colliderect(fighter.get_rect()):
                    kdir = 1 if proj.vx > 0 else -1
                    fighter.take_hit(SPECIAL_DMG, kdir)
                    proj.active = False
                    hx = fighter.x + fighter.width // 2
                    hy = fighter.y + fighter.height // 3
                    self.hit_effects.append((hx, hy, proj.color, 15))
                    break
        for p in to_remove:
            if p in self.projectiles:
                self.projectiles.remove(p)

    def _end_round_by_ko(self):
        self.match_state = 'ROUND_END'
        if self.p1.state == 'dead' and self.p2.state == 'dead':
            self.announcement = 'DRAW!'
        elif self.p1.state == 'dead':
            self.winner = self.p2.name
            self.p2.wins += 1
        else:
            self.winner = self.p1.name
            self.p1.wins += 1
        self.announcement = 'KO!'
        self.announcement_timer = 120
        self._check_match_over()

    def _end_round_by_timer(self):
        self.match_state = 'ROUND_END'
        if self.p1.health > self.p2.health:
            self.winner = self.p1.name
            self.p1.wins += 1
            self.announcement = f'{self.p1.name} WINS!'
        elif self.p2.health > self.p1.health:
            self.winner = self.p2.name
            self.p2.wins += 1
            self.announcement = f'{self.p2.name} WINS!'
        else:
            self.announcement = 'DRAW!'
        self.announcement_timer = 120
        self._check_match_over()

    def _check_match_over(self):
        wins_needed = (MAX_ROUNDS // 2) + 1
        if self.p1.wins >= wins_needed or self.p2.wins >= wins_needed:
            self.match_state = 'GAME_OVER'
            self.result = 'p1' if self.p1.wins >= wins_needed else 'p2'

    def next_round(self):
        self.round_number += 1
        p1_wins = self.p1.wins
        p2_wins = self.p2.wins
        self.p1, self.p2 = create_fighters()
        self.p1.wins = p1_wins
        self.p2.wins = p2_wins
        self.fighters = [self.p1, self.p2]
        self.projectiles = []
        self.hit_effects = []
        self.round_timer = ROUND_TIME * FPS
        self.match_state = 'FIGHTING'
        self.winner = None
        self.announcement = f'ROUND {self.round_number}'
        self.announcement_timer = 90

    def draw(self):
        draw_stage(self.screen)

        for proj in self.projectiles:
            proj.draw(self.screen)

        for x, y, c, t in self.hit_effects:
            draw_hit_effect(self.screen, x, y, c)

        for f in self.fighters:
            f.draw(self.screen, self.font_small)

        draw_hud(self.screen, self.fighters, self.round_timer,
                 self.round_number, self.fonts)

        if self.announcement and self.announcement_timer > 0:
            draw_announcement(self.screen, self.announcement, self.font_big)

        if self.match_state == 'GAME_OVER':
            self._draw_game_over()

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        go_surf = self.font_big.render('GAME OVER', True, NEON_PINK)
        cx = SCREEN_WIDTH // 2 - go_surf.get_width() // 2
        self.screen.blit(go_surf, (cx, 160))

        if self.result:
            winner_name = self.p1.name if self.result == 'p1' else self.p2.name
            w_surf = self.font_med.render(f'{winner_name} WINS!', True, NEON_YELLOW)
            wx = SCREEN_WIDTH // 2 - w_surf.get_width() // 2
            self.screen.blit(w_surf, (wx, 260))

        hint = self.font_small.render('Press ENTER to play again   ESC for menu', True, LIGHT_GRAY)
        hx = SCREEN_WIDTH // 2 - hint.get_width() // 2
        self.screen.blit(hint, (hx, 360))
