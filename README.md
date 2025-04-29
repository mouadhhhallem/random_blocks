Random Blocks Game
Random Blocks is a grid-based puzzle adventure where players navigate a character through dynamically generated mazes to reach an exit. With multiple levels, power-ups, weather effects, achievements, and a scoring system, the game becomes increasingly challenging and engaging as players progress.

🧩 Game Overview
Built with Pygame, a popular Python library for 2D game development, the game places the player in control of a character navigating a maze-like map. Players must avoid obstacles, collect power-ups, and reach the exit within a time limit. Each level introduces new challenges like expanded maps, time constraints, and environmental effects.

🎮 Core Gameplay Mechanics
🔲 Grid-Based Movement
Use arrow keys (↑ ↓ ← →) to move.

Movement is restricted to empty spaces (roads); walls block movement.

A cooldown system ensures smooth movement and prevents key spamming.

🗺️ Dynamic Map Generation
Each level features a new, randomly generated map.

The map grows with each level (adding rows and columns).

Dijkstra's algorithm ensures a valid path exists from start to finish.

⚡ Power-Ups
Speed Boost: Temporarily increases movement speed.

Extra Time: Adds 5 seconds to the timer.

Bonus Coins: Adds points to the player's score.

⏳ Time Limit
Each level has a time limit (starting at 15 seconds for Level 1).

If time runs out, the player is reset to Level 1.

🧮 Scoring System
Score formula:
Score = (Level × 2000) + (Coins × 500) - (Steps × 2)

Score is never allowed to fall below 100.

🎥 Camera System
The camera smoothly follows the player.

The grid is centered with padding and borders for aesthetics.

🌦️ Advanced Features
☁️ Weather System
Rain: Slows player movement.

Snow: Reduces visibility (not fully implemented yet).

🏆 Achievements
Unlock achievements by meeting conditions (e.g., finish a level with >10 seconds remaining).

Displayed in-game and logged in the console.

🌲 Skill Tree
Spend points to unlock upgrades:

Permanent Speed Boost

Extra Time per Level

🧍 Randomized Character Skins
Characters are randomly assigned skins from a collection of animal images at the start of each game.

💯 Score Popup Animation
At game end, a popup animates score calculation (level, coins, steps).

A reset button restarts the game.

🛠️ Technical Details
🧭 Map Generation
Combines random placement with Dijkstra’s algorithm for pathfinding.

Ensures every level is solvable.

🧰 Asset Management
Loads wall, road, door, and character images from specified directories.

Supports custom assets (characters, walls, coins, etc.).

📁 File Handling
Saves the top score to scores.txt.

Displayed in the score popup after each game session.

🧱 Modular Design
settings.py: Constants, colors, file paths.

game_logic.py: Map generation, pathfinding, drawing functions.

main.py: Game loop, input handling, scoring.

🎨 Visual and Audio Design (Planned/Optional)
Clean grid-based visuals with contrasting colors for roads, walls, and power-ups.

Doors use custom images (door_a.png, door_b.png).

Background color: Dark gray, with light brown for gaps.

Optional enhancements:

Footstep sounds

Power-up collection sounds

Background music

🚀 Potential Improvements
🔊 Audio
Add sound effects (e.g., movement, power-up collection, level completion).

Background music for immersive gameplay.

🎆 Graphics
Add animations for character movement and weather.

Use particle effects for power-ups and achievements.

🧪 More Power-Ups
Add new types like:

Invincibility

Teleportation

👥 Multiplayer Mode
Implement competitive or cooperative multiplayer functionality.

📱 Mobile Support
Adapt UI for touch controls and mobile screen sizes.
