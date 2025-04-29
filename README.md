Great! You've already created a comprehensive `.md` (Markdown) file that outlines the **Random Blocks Game**. Here's your content formatted cleanly and properly structured for better readability as a `README.md` or design document:

---

# 🎮 Random Blocks Game

**A grid-based puzzle adventure where players navigate dynamically generated mazes to reach an exit.**

With increasing difficulty across levels, power-ups, weather effects, achievements, and a scoring system, *Random Blocks* offers a progressively challenging gameplay experience.

---

## 🧩 Game Overview

Built using **Pygame**, a popular Python library for 2D game development, this game challenges players to guide their character through procedurally generated mazes.

Players must:
- Avoid obstacles
- Collect power-ups
- Reach the exit before time runs out

Each level introduces new elements such as larger maps, tighter time limits, and environmental effects.

---

## 🎮 Core Gameplay Mechanics

### 🔲 Grid-Based Movement
- Move using arrow keys: ↑ ↓ ← →
- Movement restricted to empty spaces (roads)
- Walls block movement
- Cooldown prevents input spamming

### 🗺️ Dynamic Map Generation
- Unique map per level
- Gradually increases in size (rows/columns)
- Path guaranteed via **Dijkstra’s Algorithm**

### ⚡ Power-Ups
| Power-Up       | Effect                        |
|----------------|-------------------------------|
| Speed Boost    | Temporarily increases speed   |
| Extra Time     | Adds 5 seconds to the timer   |
| Bonus Coins    | Adds points to the score      |

### ⏳ Time Limit
- Starts at 15 seconds for Level 1
- Time resets player to Level 1 if expired

### 🧮 Scoring System
```text
Score = (Level × 2000) + (Coins × 500) - (Steps × 2)
Minimum score: 100
```

### 🎥 Camera System
- Smooth following of player
- Centered view with padding and borders

---

## 🌦️ Advanced Features

### ☁️ Weather System
- **Rain**: Slows down character movement
- **Snow** *(WIP)*: Reduces visibility

### 🏆 Achievements
- Unlock by completing specific goals (e.g., finish level with >10s left)
- Displayed in-game and logged in console

### 🌲 Skill Tree
Unlock permanent upgrades using earned skill points:
- Permanent Speed Boost
- Extra Time per Level

### 🧍 Randomized Character Skins
- Players randomly assigned animal-themed skins at start of game

### 💯 Score Popup Animation
- After game ends, score calculation is animated
- Includes level, coins collected, steps taken
- Reset button restarts the game

---

## 🛠️ Technical Details

### 🧭 Map Generation
- Uses random room and corridor placement
- Ensures solvable paths using Dijkstra's algorithm

### 🧰 Asset Management
- Loads wall, road, door, coin, and character images from directories
- Supports custom assets for characters, walls, etc.

### 📁 File Handling
- Saves top score in `scores.txt`
- Top score displayed in end-game popup

### 🧱 Modular Design
- `settings.py`: Constants, colors, file paths
- `game_logic.py`: Map generation, pathfinding, drawing functions
- `main.py`: Main game loop, input handling, scoring logic

---

## 🎨 Visual and Audio Design *(Planned / Optional)*

### Visuals
- Clean grid layout with contrasting colors
- Door images: `door_a.png`, `door_b.png`
- Background: Dark gray; gaps: light brown

### Optional Enhancements
- 👣 Footstep sounds
- ⚡ Power-up collection sound
- 🎵 Background music

---

## 🚀 Potential Improvements

### 🔊 Audio
- Add sound effects for movement, power-ups, level completion
- Include background music for immersion

### 🎆 Graphics & Effects
- Animate character movement and weather
- Use particle effects for power-ups and achievements

### 🧪 More Power-Ups
- Invincibility
- Teleportation
- Wall destruction

### 👥 Multiplayer Mode
- Competitive or co-op multiplayer functionality

### 📱 Mobile Support
- Adapt UI for touch controls
- Optimize for mobile screen sizes

---
