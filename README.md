
# Go Game Project

## Overview

This project is a digital implementation of the traditional board game **Go**, designed with a user-friendly interface and robust functionality. The application allows players to engage in the strategic game of Go with features such as score tracking, territory calculation, and a visually appealing board.

## Features

- **Dynamic Game Board**: A grid-based board with interactive functionality for placing stones.
- **Score Tracking**: Real-time updates for captured stones, territory, and komi.
- **Turn Management**: Ensures proper alternation between Black and White players.
- **End-Game Scoring**: Automatic calculation of scores, including territory and komi.
- **Error Handling**: Displays warnings for invalid moves (e.g., suicide or Ko violations).
- **Timer**: Countdown timer for each player’s turn.
- **Restart and Pass Options**: Ability to reset the game or pass turns.

## Technologies Used

- **Python**: Core programming language for game logic and functionality.
- **PyQt6**: Used to build the graphical user interface (GUI).

## How to Play

1. Launch the application.
2. Choose your desired settings from the main menu.
3. Players alternate turns by placing stones on the board.
4. The game ends when both players pass consecutively. Scores are calculated based on captured stones and territory, with komi added to White’s score.

