
import pygame
from constants import *


class Projectile:
    def __init__(self, x, y, direction, color, owner_id):
        self.x = float(x)
        self.y = float(y)
        self.vx = direction * 10
        self.radius = 12
        self.color = color
        self.owner_id = owner_id
        self.active = True
        self.frame = 0

    def update(self):
        self.x += self.vx
        self.frame += 1
        if self.x < -60 or self.x > SCREEN_WIDTH + 60:
            self.active = False

    def get_rect(self):
        return pygame.Rect(
            int(self.x) - self.radius, int(self.y) - self.radius,
            self.radius * 2, self.radius * 2
        )

    def draw(self, screen):
        cx, cy = int(self.x), int(self.y)
        pulse = abs(pygame.math.Vector2(1, 0).rotate(self.frame * 10).x)
        r_glow = self.radius + int(6 + pulse * 4)

        glow_surf = pygame.Surface((r_glow * 2, r_glow * 2), pygame.SRCALPHA)
        r, g, b = self.color
        pygame.draw.circle(glow_surf, (r, g, b, 60), (r_glow, r_glow), r_glow)
        screen.blit(glow_surf, (cx - r_glow, cy - r_glow))

        pygame.draw.circle(screen, self.color, (cx, cy), self.radius)
        pygame.draw.circle(screen, WHITE, (cx, cy), self.radius // 2)


class Fighter:
    def __init__(self, player_id, x, y, color, secondary_color, name, facing):
        self.id = player_id
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = FIGHTER_WIDTH
        self.height = FIGHTER_HEIGHT

        self.color = color
        self.secondary_color = secondary_color
        self.name = name
        self.facing = facing

        self.health = MAX_HEALTH
        self.wins = 0

        self.state = 'idle'
        self.state_timer = 0
        self.is_grounded = True
        self.has_hit = False

        self.anim_frame = 0
        self.hit_flash = 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_attack_hitbox(self):
        if self.state == 'attack_light':
            w, h = 50, 22
        elif self.state == 'attack_heavy':
            w, h = 70, 32
        elif self.state == 'attack_kick':
            w, h = 65, 28
        else:
            return None

        if self.facing == 1:
            hx = self.x + self.width
        else:
            hx = self.x - w
        hy = self.y + 25
        return pygame.Rect(int(hx), int(hy), w, h)

    def is_attacking(self):
        return self.state in ('attack_light', 'attack_heavy', 'attack_kick', 'attack_special')

    def is_blocking(self):
        return self.state == 'block'

    def apply_action(self, action):
        """Apply an input action dict. Returns a Projectile or None."""
        if self.state in ('hitstun', 'dead'):
            return None

        if self.is_attacking() and self.state_timer > 0:
            if action.get('right'):
                self.vx = WALK_SPEED * 0.3
            elif action.get('left'):
                self.vx = -WALK_SPEED * 0.3
            return None

        new_proj = None

        if action.get('special') and self.is_grounded and self.state != 'attack_special':
            self.state = 'attack_special'
            self.state_timer = 30
            self.has_hit = False
            if self.facing == 1:
                px = self.x + self.width + 5
            else:
                px = self.x - 5
            py = self.y + 28
            new_proj = Projectile(px, py, self.facing, self.color, self.id)

        elif action.get('heavy') and not self.is_attacking():
            self.state = 'attack_heavy'
            self.state_timer = 25
            self.has_hit = False

        elif action.get('kick') and not self.is_attacking():
            self.state = 'attack_kick'
            self.state_timer = 18
            self.has_hit = False

        elif action.get('light') and not self.is_attacking():
            self.state = 'attack_light'
            self.state_timer = 12
            self.has_hit = False

        elif action.get('up') and self.is_grounded:
            self.vy = JUMP_SPEED
            self.is_grounded = False
            self.state = 'jump'
            self.state_timer = 0

        elif action.get('down') and self.is_grounded:
            self.state = 'crouch'
            self.vx = 0

        elif action.get('block') and self.is_grounded:
            self.state = 'block'
            self.vx = 0

        elif action.get('right'):
            self.vx = WALK_SPEED
            if self.is_grounded and not self.is_attacking():
                self.state = 'walk'

        elif action.get('left'):
            self.vx = -WALK_SPEED
            if self.is_grounded and not self.is_attacking():
                self.state = 'walk'

        else:
            if self.is_grounded and not self.is_attacking() and self.state != 'hitstun':
                self.state = 'idle'
            self.vx = 0

        return new_proj

    def update(self):
        if not self.is_grounded:
            self.vy += GRAVITY
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED

        self.x += self.vx
        self.y += self.vy

        ground_level = GROUND_Y - self.height
        if self.y >= ground_level:
            self.y = ground_level
            self.vy = 0
            if not self.is_grounded:
                self.is_grounded = True
                if self.state == 'jump':
                    self.state = 'idle'

        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

        if self.state_timer > 0:
            self.state_timer -= 1
        else:
            if self.state in ('attack_light', 'attack_heavy', 'attack_kick', 'attack_special'):
                self.state = 'idle'
                self.has_hit = False
            elif self.state == 'hitstun':
                self.state = 'idle'

        self.anim_frame += 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

        self.vx *= 0.75

    def take_hit(self, damage, knockback_dir):
        if self.state == 'dead':
            return

        if self.is_blocking():
            damage = max(1, int(damage * BLOCK_REDUCTION))

        self.health = max(0, self.health - damage)
        self.hit_flash = 10

        if not self.is_blocking():
            self.vx = knockback_dir * KNOCKBACK
            self.state = 'hitstun'
            self.state_timer = HITSTUN_FRAMES

        if self.health <= 0:
            self.state = 'dead'
            self.state_timer = 9999

    def draw(self, screen, font_small):
        x, y = int(self.x), int(self.y)
        w, h = self.width, self.height

        flash = self.hit_flash % 2 == 1
        c = WHITE if flash else self.color
        sc = WHITE if flash else self.secondary_color

        sway_y = 0
        if self.state == 'idle':
            sway_y = int(1.5 * abs(pygame.math.Vector2(0, 1).rotate(self.anim_frame * 3).y) - 0.75)

        crouch = self.state == 'crouch'
        body_compress = 15 if crouch else 0

        # Shadow
        shadow = pygame.Surface((w + 10, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, w + 10, 12))
        screen.blit(shadow, (x - 5, GROUND_Y - 10))

        # Legs
        leg_bob = (self.anim_frame // 6) % 2 == 0 and self.state == 'walk'
        left_leg_dy = -4 if leg_bob else 0
        right_leg_dy = 4 if leg_bob else 0
        leg_top = y + h - 35 + body_compress
        pygame.draw.rect(screen, c, (x + 8, leg_top + left_leg_dy, 18, 35 - body_compress))
        pygame.draw.rect(screen, c, (x + w - 26, leg_top + right_leg_dy, 18, 35 - body_compress))
        # Shoes
        shoe_r = pygame.Rect(x + w - 28, y + h - 10, 22, 10)
        shoe_l = pygame.Rect(x + 6, y + h - 10, 22, 10)
        pygame.draw.rect(screen, sc, shoe_l)
        pygame.draw.rect(screen, sc, shoe_r)

        # Torso
        torso_h = 38 - body_compress
        torso_y = y + 28 + sway_y + body_compress
        pygame.draw.rect(screen, c, (x + 5, torso_y, w - 10, torso_h))
        pygame.draw.rect(screen, sc, (x + 5, torso_y + torso_h - 10, w - 10, 10))

        # Punch extension
        punch_ext = 0
        kick_ext = 0
        if self.state == 'attack_light' and self.state_timer < 8:
            punch_ext = 22
        elif self.state == 'attack_heavy' and self.state_timer < 18:
            punch_ext = 36
        if self.state == 'attack_kick' and self.state_timer < 12:
            kick_ext = 32

        # Arms
        arm_y = torso_y + 5
        if self.facing == 1:
            pygame.draw.rect(screen, c, (x + w - 5, arm_y, 10 + punch_ext, 16))
            pygame.draw.rect(screen, c, (x - 5, arm_y + 4, 10, 12))
        else:
            pygame.draw.rect(screen, c, (x - 5 - punch_ext, arm_y, 10 + punch_ext, 16))
            pygame.draw.rect(screen, c, (x + w - 5, arm_y + 4, 10, 12))

        # Kick extension
        if kick_ext > 0:
            leg_ext_y = y + h - 22
            if self.facing == 1:
                pygame.draw.rect(screen, c, (x + w - 5, leg_ext_y, kick_ext, 16))
            else:
                pygame.draw.rect(screen, c, (x - kick_ext + 5, leg_ext_y, kick_ext, 16))

        # Head
        head_r = 18
        head_cx = x + w // 2
        head_cy = torso_y - head_r + sway_y
        pygame.draw.circle(screen, c, (head_cx, head_cy), head_r)
        pygame.draw.rect(screen, sc, (head_cx - head_r, head_cy - head_r + 2, head_r * 2, 8))

        eye_offset = 6 if self.facing == 1 else -6
        if self.state == 'dead':
            for dx, dy, ex, ey in [(-4, -6, 4, 2), (4, -6, -4, 2)]:
                pygame.draw.line(screen, RED,
                                 (head_cx + eye_offset + dx, head_cy + dy),
                                 (head_cx + eye_offset + ex, head_cy + ey), 2)
        else:
            pygame.draw.circle(screen, WHITE, (head_cx + eye_offset, head_cy - 2), 4)
            pygame.draw.circle(screen, BLACK, (head_cx + eye_offset + (1 if self.facing == 1 else -1), head_cy - 2), 2)

        # Block shield
        if self.state == 'block':
            shield_x = (x + w + 2) if self.facing == 1 else (x - 18)
            shield_rect = pygame.Rect(shield_x, y + 15, 16, 50)
            pygame.draw.rect(screen, CYAN, shield_rect, border_radius=4)
            pygame.draw.rect(screen, WHITE, shield_rect, 2, border_radius=4)

        # Name tag
        name_surf = font_small.render(self.name, True, WHITE)
        screen.blit(name_surf, (x + w // 2 - name_surf.get_width() // 2, y - 22))
