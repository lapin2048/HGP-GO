from PyQt6.QtWidgets import QFrame, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush
from piece import Piece
from game_logic import GoGame

class Board(QFrame):
    timerUpdated = pyqtSignal(int)
    positionClicked = pyqtSignal(str)
    clickLocationSignal = pyqtSignal(str)
    updateTimerSignal = pyqtSignal(int)  # Declare the signal
    updateScoresSignal = pyqtSignal(int, int) # Declare the signal
    updateCapturedStonesSignal = pyqtSignal(int, int)
    updateTerritorySignal = pyqtSignal(int, int)


    GRID_SIZE = 9  # Default 9x9 board

    def __init__(self, parent=None, scoreboard=None):
        super().__init__(parent)
        self.margin = 40
        self.scoreboard = scoreboard
        self.initialize_board()
        self.pending_moves = []
        self.current_move_index = -1
        self.hovered_cell = (-1, -1)
        self.player_turn = 1
        self.pass_count = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimer)
        self.remaining_time = 30

        # Load graphics
        self.bg_image = QPixmap("Assets/background.png")
        self.white_stone = QPixmap("Assets/white.png")
        self.black_stone = QPixmap("Assets/black.png")

        # Initialize game logic
        self.logic = GoGame(self.grid, self.GRID_SIZE)
        self.setMouseTracking(True)

    def initialize_board(self):
        self.grid = [[Piece(0, r, c) for c in range(self.GRID_SIZE)] for r in range(self.GRID_SIZE)]

    def square_width(self):
        return self.contentsRect().width() / (self.GRID_SIZE - 1)

    def square_height(self):
        return self.contentsRect().height() / (self.GRID_SIZE - 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_background(painter)
        self.draw_grid(painter)
        self.draw_stones(painter)
        self.draw_hovered_stone(painter)

    def draw_background(self, painter):
        if not self.bg_image.isNull():
            painter.drawPixmap(self.rect(), self.bg_image)

    def mousePressEvent(self, event):
        grid_x = round(event.position().x() / self.square_width())
        grid_y = round(event.position().y() / self.square_height())
        if self.logic.is_within_bounds(grid_y, grid_x):
            self.positionClicked.emit(f"Clicked on cell {grid_y}, {grid_x}")
            self.clickLocationSignal.emit(f"{grid_y}, {grid_x}")

        if self.logic.is_valid_move(grid_y, grid_x):
            move = {"row": grid_y, "col": grid_x, "player": self.player_turn}
            self.pending_moves.append(move)
            self.current_move_index = len(self.pending_moves) - 1
            self.update()

    def confirm_move(self):
        if self.current_move_index == -1:
            return

        move = self.pending_moves.pop(self.current_move_index)
        row, col = move["row"], move["col"]
        self.grid[row][col].change_state(self.player_turn)

        captured = self.logic.execute_move(row, col, self.player_turn)
        if captured:
            self.handle_captures(captured)

        self.switch_turn()
        self.update()

    def handle_captures(self, captured_positions):
        for row, col in captured_positions:
            self.grid[row][col].change_state(0)
        self.update()

    def switch_turn(self):
        self.player_turn = 3 - self.player_turn
        self.pass_count = 0

    def draw_grid(self, painter):
        painter.setPen(Qt.GlobalColor.black)
        for col in range(self.GRID_SIZE):
            x = int(col * self.square_width())
            painter.drawLine(x, 0, x, self.height())

        for row in range(self.GRID_SIZE):
            y = int(row * self.square_height())
            painter.drawLine(0, y, self.width(), y)


    def draw_stones(self, painter):
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                piece = self.grid[row][col]
                if piece.state == 1:
                    stone = self.white_stone
                elif piece.state == 2:
                    stone = self.black_stone
                else:
                    continue

                center_x = col * self.square_width()
                center_y = row * self.square_height()
                size = min(self.square_width(), self.square_height()) * 0.8
                painter.drawPixmap(center_x - size / 2, center_y - size / 2, size, size, stone)

    def draw_hovered_stone(self, painter):
        row, col = self.hovered_cell
        if row == -1 or col == -1:
            return

        stone = self.white_stone if self.player_turn == 1 else self.black_stone
        painter.setOpacity(0.5)
        size = int(min(self.square_width(), self.square_height()) * 0.8)
        center_x = int(col * self.square_width())
        center_y = int(row * self.square_height())
        painter.drawPixmap(center_x - size // 2, center_y - size // 2, size, size, stone)
        painter.setOpacity(1.0)


    def mouseMoveEvent(self, event):
        grid_x = round(event.position().x() / self.square_width())
        grid_y = round(event.position().y() / self.square_height())

        if self.logic.is_valid_move(grid_y, grid_x):
            self.hovered_cell = (grid_y, grid_x)
        else:
            self.hovered_cell = (-1, -1)
        self.update()

    def start_game(self):
        self.initialize_board()
        self.player_turn = 1
        self.pass_count = 0
        self.update()

    def end_game(self):
        scores = self.logic.calculate_scores()
        black_score = scores['black']
        white_score = scores['white']

        if black_score > white_score:
            message = f"Black wins by {black_score - white_score} points!"
        elif white_score > black_score:
            message = f"White wins by {white_score - black_score} points!"
        else:
            message = "The game is a draw!"

        QMessageBox.information(self, "Game Over", message)
        self.timerUpdated.emit(black_score)

    def pass_turn(self):
        self.pass_count += 1
        if self.pass_count >= 2:
            self.end_game()
        else:
            self.switch_turn()
            self.update()


    def startTimer(self):
        """Start a countdown timer."""
        self.remaining_time = 30
        self.timer.start(1000)  # Timer updates every second

    def updateTimer(self):
        """Update the timer and emit the signal."""
        self.remaining_time -= 1
        self.updateTimerSignal.emit(self.remaining_time)

        if self.remaining_time <= 0:
            self.timer.stop()
            print("Time's up!")

    def updateScores(self, player1_score, player2_score):
        # Emit updated scores
        self.updateScoresSignal.emit(player1_score, player2_score)


    def handleCapturedPieces(self, captured_positions):
        """Handle and update captured pieces."""
        captured_white = 0
        captured_black = 0

        for row, col in captured_positions:
            piece = self.board[row][col]
            if piece.state == 1:  # White stone
                captured_white += 1
            elif piece.state == 2:  # Black stone
                captured_black += 1

            piece.state = 0  # Clear the piece from the board

        # Emit the signal with updated counts
        self.updateCapturedStonesSignal.emit(captured_white, captured_black)
        self.update()


    def updateTerritory(self, territory_p1, territory_p2):
        """Update territory counts for both players."""
        self.label_territoryP1.setText(f"Territory Player 1 (White): {territory_p1}")
        self.label_territoryP2.setText(f"Territory Player 2 (Black): {territory_p2}")
        self.update()