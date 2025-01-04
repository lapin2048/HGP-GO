from PyQt6.QtWidgets import QFrame, QMessageBox, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPainter, QPixmap, QColor


class Board(QFrame):
    # Signals for UI interaction
    positionClicked = pyqtSignal(str)
    updateTimerSignal = pyqtSignal(int)
    updateCapturedStonesSignal = pyqtSignal(int, int)
    updateScoresSignal = pyqtSignal(dict)  # Signal for score updates

    GRID_SIZE = 8  # Default to 7x7 board

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

        self.setMouseTracking(True)  # Enable mouse hover detection
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(200, 200)  # Set a minimum size for the board

        # Load graphics
        self.bg_image = QPixmap("../Assets/background.png")
        self.white_stone = QPixmap("../Assets/white.png")
        self.black_stone = QPixmap("../Assets/black.png")

    def resizeEvent(self, event):
        """Ensure the board maintains a 1:1 aspect ratio when resized."""
        size = min(self.width(), self.height())
        self.resize(size, size)
        super().resizeEvent(event)

    def sizeHint(self):
        """Provide a preferred size for the board."""
        return QSize(600, 600)  # Default size

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
        # Draw the grid lines
        pen = painter.pen()
        dark_brown = QColor(51, 25, 0)  # Dark brown RGB color
        pen.setColor(dark_brown)  # Set the grid line color
        pen.setWidth(2)  # Set the line thickness for grid lines
        painter.setPen(pen)

        for col in range(self.GRID_SIZE):
            x = int(self.margin + col * self.square_width())
            painter.drawLine(x, self.margin, x, self.height() - self.margin)

        for row in range(self.GRID_SIZE):
            y = int(self.margin + row * self.square_height())
            painter.drawLine(self.margin, y, self.width() - self.margin, y)

        # Draw the outline around the board
        outline_pen = painter.pen()
        mahogany_brown = QColor(102, 64, 0)  # Mahogany brown RGB color
        outline_pen.setColor(mahogany_brown)  # Set the outline color
        outline_pen.setWidth(4)  # Set the outline thickness
        painter.setPen(outline_pen)
        painter.drawRect(
            self.margin,
            self.margin,
            self.width() - 2 * self.margin,
            self.height() - 2 * self.margin,
        )

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
        """Draw the stones on the board based on the current game state."""
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                piece = self.logic.get_piece_at(row, col)
                if piece == 1:
                    stone = self.black_stone
                elif piece == -1:
                    stone = self.white_stone
                else:
                    continue

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
            if captured_positions is not None:
                self.update()

                # Calculate updated scores and captured stones
                scores = self.logic.calculate_scores()
                print(f"Updated Scores: {scores}")  # Debug
                captured = self.logic.captured_stones
                print(f"Captured Stones: {captured}")  # Debug

                self.updateScoresSignal.emit(scores)  # Emit scores as a dictionary
                self.timer.stop()  # Stop the timer for the current player
                self.remaining_time = 30  # Reset the timer for the next player
                self.timer.start(1000)  # Restart the timer
                self.updateCapturedStonesSignal.emit(captured[1], captured[-1])  # Emit captured stones
            else:
                QMessageBox.warning(self, "Invalid Move", "This move is not allowed.")

    def mouseMoveEvent(self, event):
        grid_x = round((event.position().x() - self.margin) / self.square_width())
        grid_y = round((event.position().y() - self.margin) / self.square_height())

        if self.logic.is_within_bounds(grid_y, grid_x):
            if self.hovered_cell != (grid_y, grid_x):
                self.hovered_cell = (grid_y, grid_x)
                print(f"Hovering over cell: ({grid_y}, {grid_x})")  # Debug
                self.update()
        else:
            self.hovered_cell = (-1, -1)
            self.update()

    def start_game(self):
        self.logic.reset_game()
        self.remaining_time = 30
        self.updateTimerSignal.emit(self.remaining_time)
        self.timer.start(1000)
        self.update()

    def end_game(self):
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
        self.remaining_time -= 1
        self.updateTimerSignal.emit(self.remaining_time)

        if self.remaining_time <= 0:
            self.timer.stop()
            self.end_game()

    def pass_turn(self):
        self.timer.stop()
        self.remaining_time = 30
        self.updateTimerSignal.emit(self.remaining_time)
        game_over = self.logic.pass_turn()
        if game_over:
            self.end_game()
        else:
            self.timer.start(1000)
            self.update()

    def reset(self):
        print("Resetting the board...")
        self.logic.reset_game()
        self.update()
