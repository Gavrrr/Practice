
import random
from constants import *


def compute_ai(game_state, difficulty, last_action, frame_count):
    """Compute AI input action for player 2."""
    p1 = game_state['fighters'][0]
    ai = game_state['fighters'][1]

    action = {
        'up': False, 'down': False, 'left': False, 'right': False,
        'light': False, 'heavy': False, 'kick': False,
        'special': False, 'block': False
    }

    if game_state['match_state'] != 'FIGHTING':
        return action
    if ai.state in ('hitstun', 'dead'):
        return action

    dist = abs(p1.x - ai.x)
    facing_dir = 1 if ai.x < p1.x else -1

    rate = {'EASY': 50, 'MEDIUM': 20, 'HARD': 8}[difficulty]

    if frame_count % rate != 0:
        action['left'] = last_action.get('left', False)
        action['right'] = last_action.get('right', False)
        action['block'] = last_action.get('block', False)
        return action

    r = random.random()
    p1_attacking = (p1.is_attacking() or len(game_state['projectiles']) > 0)

    if difficulty == 'EASY':
        if r < 0.3:
            action['left'] = True
        elif r < 0.6:
            action['right'] = True
        elif dist < 100:
            if r < 0.8:
                action['light'] = True
            else:
                action['kick'] = True
        if r > 0.95:
            action['up'] = True

    elif difficulty == 'MEDIUM':
        if p1_attacking and r < 0.4:
            action['block'] = True
        elif dist > 180:
            if facing_dir == 1:
                action['right'] = True
            else:
                action['left'] = True
            if r < 0.15:
                action['special'] = True
        elif dist < 90:
            if r < 0.35:
                action['light'] = True
            elif r < 0.65:
                action['kick'] = True
            else:
                action['heavy'] = True
        else:
            if facing_dir == 1:
                action['right'] = True
            else:
                action['left'] = True
        if r > 0.9:
            action['up'] = True

    elif difficulty == 'HARD':
        if p1_attacking and r < 0.75:
            action['block'] = True
        elif dist > 220:
            if r < 0.35:
                action['special'] = True
            else:
                if facing_dir == 1:
                    action['right'] = True
                else:
                    action['left'] = True
            if r > 0.85:
                action['up'] = True
        elif dist > 90:
            if facing_dir == 1:
                action['right'] = True
            else:
                action['left'] = True
            if r < 0.3:
                action['kick'] = True
        else:
            if p1.state == 'hitstun':
                action['heavy'] = True
            else:
                if r < 0.35:
                    action['light'] = True
                elif r < 0.55:
                    action['crouch'] = True
                elif r < 0.75:
                    action['kick'] = True
                else:
                    action['heavy'] = True

    return action
