# Street Brawler — Python / Pygame

A Street Fighter-style 2D fighting game written in Python using Pygame.

## Requirements

- Python 3.8 or newer
- pygame 2.5+

## Setup & Run

```bash
# 1. Install pygame
pip install pygame

# 2. Run the game
cd street_brawler_py
python main.py
```

## Game Modes

| Mode | Description |
|---|---|
| 2 Players | Both players share the same keyboard |
| VS Computer | Play against an AI opponent |

## Difficulty (VS Computer)

| Level | Behaviour |
|---|---|
| Easy | Slow reactions, mostly random movement |
| Medium | Blocks attacks, approaches and combos occasionally |
| Hard | Aggressive, high block rate, footsie range tactics |

## Controls

### Player 1
| Key | Action |
|---|---|
| A / D | Move left / right |
| W | Jump |
| S | Crouch / Block |
| F | Light punch (5 dmg) |
| G | Heavy punch (12 dmg) |
| H | Kick (8 dmg) |
| Space | Special move — energy projectile (15 dmg) |

### Player 2 (PvP only)
| Key | Action |
|---|---|
| ← / → | Move left / right |
| ↑ | Jump |
| ↓ | Crouch / Block |
| L | Light punch |
| ; | Heavy punch |
| ' | Kick |
| Enter | Special move |

## Rules

- Best of 3 rounds
- Each round lasts 60 seconds
- If the timer runs out, the fighter with more health wins the round
- Blocking reduces incoming damage by 80%
- First to win 2 rounds wins the match

## Files

```
street_brawler_py/
├── main.py        — Entry point and main loop
├── menu.py        — Main menu screen
├── game.py        — Game state, round management, collision logic
├── fighter.py     — Fighter class + Projectile class
├── ai.py          — AI opponent logic (3 difficulty levels)
├── renderer.py    — Stage, HUD, and effect drawing
├── constants.py   — Tuning values, colours, screen size
└── requirements.txt
```
