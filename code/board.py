from PyQt6.QtWidgets import QFrame, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPixmap


class Board(QFrame):
    # Signals for UI interaction
    positionClicked = pyqtSignal(str)
    updateTimerSignal = pyqtSignal(int)
    updateCapturedStonesSignal = pyqtSignal(int, int)
    updateScoresSignal = pyqtSignal(dict)  # Signal now accepts a dictionary
    updateCapturedStonesSignal = pyqtSignal(int, int)  # Signal for captured stones
    GRID_SIZE = 9  # Default 9x9 board

    def __init__(self, parent=None, logic=None, score_board=None):
        super().__init__(parent)
        if logic is None:
            raise ValueError("Game logic instance must be provided.")
        
        self.margin = 40
        self.logic = logic
        self.hovered_cell = (-1, -1)
        self.remaining_time = 30
        self.score_board = score_board
        # Timer for game countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimer)

        # Load assets
        self.bg_image = QPixmap("Assets/background.png")
        self.white_stone = QPixmap("Assets/white.png")
        self.black_stone = QPixmap("Assets/black.png")

        self.setMouseTracking(True)  # Enable mouse hover detection

    def square_width(self):
        return (self.contentsRect().width() - 2 * self.margin) / (self.GRID_SIZE - 1)

    def square_height(self):
        return (self.contentsRect().height() - 2 * self.margin) / (self.GRID_SIZE - 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_background(painter)
        self.draw_grid(painter)
        self.draw_stones(painter)
        self.draw_hover(painter)  

    def draw_background(self, painter):
        if not self.bg_image.isNull():
            painter.drawPixmap(
                self.margin, self.margin,
                self.width() - 2 * self.margin,
                self.height() - 2 * self.margin,
                self.bg_image
            )

    def draw_grid(self, painter):
        painter.setPen(Qt.GlobalColor.black)
        for col in range(self.GRID_SIZE):
            x = int(self.margin + col * self.square_width())
            painter.drawLine(x, self.margin, x, self.height() - self.margin)

        for row in range(self.GRID_SIZE):
            y = int(self.margin + row * self.square_height())
            painter.drawLine(self.margin, y, self.width() - self.margin, y)

    def draw_hover(self, painter):
        """Draw a highlight on the hovered cell."""
        if self.hovered_cell != (-1, -1):  # Ensure the hover is valid
            row, col = self.hovered_cell
            center_x = int(self.margin + col * self.square_width())
            center_y = int(self.margin + row * self.square_height())
            size = int(min(self.square_width(), self.square_height()) * 0.8)

            # Set semi-transparent brush for the hover effect
            painter.setBrush(Qt.GlobalColor.lightGray)
            painter.setOpacity(0.5)
            painter.drawEllipse(center_x - size // 2, center_y - size // 2, size, size)
            painter.setOpacity(1.0)  # Reset opacity

    def draw_stones(self, painter):
        """
        Draw the stones on the board based on the current game state.
        """
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                piece = self.logic.get_piece_at(row, col)  # Use the logic to get the state of the piece
                if piece == 1:
                    stone = self.black_stone
                elif piece == -1:
                    stone = self.white_stone
                else:
                    continue  # No stone at this position

                center_x = int(self.margin + col * self.square_width())
                center_y = int(self.margin + row * self.square_height())
                size = int(min(self.square_width(), self.square_height()) * 0.8)
                painter.drawPixmap(center_x - size // 2, center_y - size // 2, size, size, stone)


    def mousePressEvent(self, event):
        grid_x = round((event.position().x() - self.margin) / self.square_width())
        grid_y = round((event.position().y() - self.margin) / self.square_height())
        self.positionClicked.emit(f"({grid_y}, {grid_x})")
        if self.logic.is_within_bounds(grid_y, grid_x):
            captured_positions = self.logic.place_stone(grid_y, grid_x)
            if captured_positions is not None:  # Valid move
                self.update()

                # Calculate updated scores and captured stones
                scores = self.logic.calculate_scores()
                print(f"Updated Scores: {scores}")  # Debug
                captured = self.logic.captured_stones
                print(f"Captured Stones: {captured}")  # Debug

                # Emit the signals
                self.updateScoresSignal.emit(scores)  # Emit scores as a dictionary
                self.timer.stop()  # Stop the timer for the current player
                self.remaining_time = 30  # Reset the timer for the next player
                self.timer.start(1000)  # Restart the timer
                self.updateCapturedStonesSignal.emit(captured[1], captured[-1])  # Emit captured stones
            else:
                QMessageBox.warning(self, "Invalid Move", "This move is not allowed.")


    def mouseMoveEvent(self, event):
        """Track the mouse position and update the hovered cell."""
        grid_x = round((event.position().x() - self.margin) / self.square_width())
        grid_y = round((event.position().y() - self.margin) / self.square_height())

        # Check if the hover is within bounds
        if self.logic.is_within_bounds(grid_y, grid_x):
            if self.hovered_cell != (grid_y, grid_x):  # Only update if the hovered cell changes
                self.hovered_cell = (grid_y, grid_x)
                print(f"Hovering over cell: ({grid_y}, {grid_x})")  # Debug statement
                self.update()  # Trigger a repaint
        else:
            self.hovered_cell = (-1, -1)  # Reset if out of bounds
            self.update()  # Trigger a repaint

    def start_game(self):
        """Initialize a new game."""
        self.logic.reset_game()
        self.remaining_time = 30  # Reset timer for White
        self.updateTimerSignal.emit(self.remaining_time)
        self.timer.start(1000)  # Start the timer for the first turn
        self.update()  # Redraw the board
        

    def end_game(self):
        """Handle end of game logic."""
        scores = self.logic.calculate_scores()
        black_score = scores["black"]
        white_score = scores["white"]

        if black_score > white_score:
            message = f"Black wins by {black_score - white_score} points!"
        elif white_score > black_score:
            message = f"White wins by {white_score - black_score} points!"
        else:
            message = "The game is a draw!"

        QMessageBox.information(self, "Game Over", message)

    def updateTimer(self):
        """Update game timer."""
        self.remaining_time -= 1
        self.updateTimerSignal.emit(self.remaining_time)

        if self.remaining_time <= 0:
            self.timer.stop()
            self.end_game()  # Call the end-game method


    def pass_turn(self):
        """Pass the current player's turn."""
        self.timer.stop()
        self.remaining_time = 30  # Reset the timer for the next player
        self.updateTimerSignal.emit(self.remaining_time)
        game_over = self.logic.pass_turn()  # Check for game over logic
        if game_over:
            self.end_game()
        else:
            self.timer.start(1000)  # Restart the timer for the next player
            self.update()  # Redraw the board



    def reset(self):
        """Reset the board state and UI."""
        print("Resetting the board...")  # Debug statement
        self.logic.reset_game()  # Reset the game logic
        self.update()  # Redraw the board to clear the UI
