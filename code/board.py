from PyQt6.QtWidgets import QFrame, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize, QPropertyAnimation
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
from piece import Piece
from game_logic import GoGame


class Board(QFrame):
    updateTimerSignal = pyqtSignal(int)
    clickLocationSignal = pyqtSignal(str)

    boardWidth = 9  # 9x9 Goban
    boardHeight = 9
    player_turn = 1  # 1 for white, 2 for black
    isStarted = False

    def __init__(self, parent=None, scoreBoard=None):
        super().__init__(parent)
        self.margin = 40
        self.scoreBoard = scoreBoard  # Reference to ScoreBoard widget
        self.initBoard()

        # Load assets
        self.background_pixmap = QPixmap("Assets/background.png")
        self.white_stone_pixmap = QPixmap("Assets/white.png")
        self.black_stone_pixmap = QPixmap("Assets/black.png")

        # Validate assets
        if self.background_pixmap.isNull():
            print("Failed to load background.png")
        if self.white_stone_pixmap.isNull():
            print("Failed to load white.png")
        if self.black_stone_pixmap.isNull():
            print("Failed to load black.png")

        self.captured_pieces = []  # List to track captured pieces
        self.hover_row = -1  # Default no hover
        self.hover_col = -1  # Default no hover
        self.setMouseTracking(True)  # Enable hover detection
        self.logic = GoGame((self.boardWidth))

    def initBoard(self):
        """Initializes the board."""
        self.boardArray = [[0 for _ in range(self.boardWidth)] for _ in range(self.boardHeight)]
        self.printBoardArray()

    def printBoardArray(self):
        """Prints the boardArray for debugging."""
        print("boardArray:")
        print('\n'.join(['\t'.join(map(str, row)) for row in self.boardArray]))

    def squareWidth(self):
        return self.contentsRect().width() / (self.boardWidth - 1)

    def squareHeight(self):
        return self.contentsRect().height() / (self.boardHeight - 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawBackground(painter)
        self.drawBoardLines(painter)
        self.drawStars(painter)
        self.drawPieces(painter)
        self.drawHoverPiece(painter)
        self.drawCapturedPieces(painter)

    def drawBackground(self, painter):
        if not self.background_pixmap.isNull():
            painter.drawPixmap(self.rect(), self.background_pixmap)

    def mousePressEvent(self, event):
        square_width = self.squareWidth()
        square_height = self.squareHeight()
        col = round(event.position().x() / square_width)
        row = round(event.position().y() / square_height)

        if self.logic.valid_position(row, col) and self.boardArray[row][col] == 0:
            self.boardArray[row][col] = self.player_turn
            captured_positions = self.logic.place_piece(row, col, self.player_turn)
            if captured_positions:
                self.handleCapturedPieces(captured_positions)

            # Toggle turn
            self.player_turn = 1 if self.player_turn == 2 else 2
            self.update()

    def mouseMoveEvent(self, event):
        square_width = self.squareWidth()
        square_height = self.squareHeight()
        col = round(event.position().x() / square_width)
        row = round(event.position().y() / square_height)

        if self.logic.valid_position(row, col) and self.boardArray[row][col] == 0:
            self.hover_row, self.hover_col = row, col
        else:
            self.hover_row, self.hover_col = -1, -1

        self.update()

    def drawBoardLines(self, painter):
        painter.setPen(Qt.GlobalColor.black)
        square_width = self.squareWidth()
        square_height = self.squareHeight()

        for col in range(self.boardWidth):
            x = int(col * square_width)  # Convert to integer
            painter.drawLine(x, 0, x, self.height())

        for row in range(self.boardHeight):
            y = int(row * square_height)  # Convert to integer
            painter.drawLine(0, y, self.width(), y)


    def drawStars(self, painter):
        star_positions = [(2, 2), (6, 2), (4, 4), (2, 6), (6, 6)]
        painter.setBrush(Qt.GlobalColor.black)
        for row, col in star_positions:
            x = col * self.squareWidth()
            y = row * self.squareHeight()
            size = min(self.squareWidth(), self.squareHeight()) * 0.1
            painter.drawEllipse(QPoint(int(x), int(y)), int(size), int(size))

    def drawPieces(self, painter):
        square_width = self.squareWidth()
        square_height = self.squareHeight()
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                if self.boardArray[row][col] == 1:
                    pixmap = self.white_stone_pixmap
                elif self.boardArray[row][col] == 2:
                    pixmap = self.black_stone_pixmap
                else:
                    continue
                x = col * square_width - square_width / 2
                y = row * square_height - square_height / 2
                painter.drawPixmap(int(x), int(y), int(square_width), int(square_height), pixmap)

    def drawHoverPiece(self, painter):
        if self.hover_row == -1 or self.hover_col == -1:
            return
        pixmap = self.white_stone_pixmap if self.player_turn == 1 else self.black_stone_pixmap
        square_width = self.squareWidth()
        square_height = self.squareHeight()
        x = self.hover_col * square_width - square_width / 2
        y = self.hover_row * square_height - square_height / 2
        painter.setOpacity(0.5)
        painter.drawPixmap(int(x), int(y), int(square_width), int(square_height), pixmap)
        painter.setOpacity(1.0)

    def drawCapturedPieces(self, painter):
        for piece in self.captured_pieces:
            x, y = piece['x'], piece['y']
            pixmap = self.white_stone_pixmap if piece['player'] == 1 else self.black_stone_pixmap
            painter.drawPixmap(int(x), int(y), int(self.squareWidth()), int(self.squareHeight()), pixmap)

    def handleCapturedPieces(self, captured_positions):
        """
        Animate and erase captured stones.
        :param captured_positions: List of (row, col) tuples representing captured stones.
        """
        for row, col in captured_positions:
            # Create a QLabel to represent the stone being removed
            stone_label = QLabel(self)
            square_width = self.squareWidth()
            square_height = self.squareHeight()
            x = col * square_width - square_width / 2
            y = row * square_height - square_height / 2

            stone_label.setGeometry(int(x), int(y), int(square_width), int(square_height))
            stone_label.setPixmap(
                self.white_stone_pixmap if self.boardArray[row][col] == 1 else self.black_stone_pixmap
            )
            stone_label.setScaledContents(True)
            stone_label.show()

            # Add an opacity effect for the fade-out
            opacity_effect = QGraphicsOpacityEffect()
            stone_label.setGraphicsEffect(opacity_effect)

            # Animate the opacity
            animation = QPropertyAnimation(opacity_effect, b"opacity")
            animation.setDuration(500)  # Animation duration in milliseconds
            animation.setStartValue(1.0)  # Fully visible
            animation.setEndValue(0.0)  # Fully transparent
            animation.finished.connect(lambda: self.finishEraseAnimation(stone_label, row, col))
            animation.start()

    def finishEraseAnimation(self, stone_label, row, col):
        """
        Cleanup after the erase animation finishes.
        :param stone_label: The QLabel of the captured stone.
        :param row: Row of the erased stone.
        :param col: Column of the erased stone.
        """
        stone_label.deleteLater()  # Remove the QLabel
        self.boardArray[row][col] = 0  # Clear the logical board state
        self.update()  # Repaint the board

    def start(self):
        """
        Starts a new game by initializing the board and resetting all variables.
        """
        # Reset logical board state
        self.boardArray = [[0 for _ in range(self.boardWidth)] for _ in range(self.boardHeight)]
        
        # Clear captured pieces
        self.captured_pieces = []
        
        # Reset player turn to White (or the default starting player)
        self.player_turn = 1  # 1 for White, 2 for Black
        
        # Reset hover position
        self.hover_row = -1
        self.hover_col = -1
        
        # Indicate that the game has started
        self.isStarted = True

        # Update the ScoreBoard if linked
        if self.scoreBoard:
            self.scoreBoard.updateTurn(self.player_turn)
            self.scoreBoard.updatePrisoners(0, 0)  # Reset captured stones
            self.scoreBoard.updateTerritory(0, 0)  # Reset territory scores
        
        # Print debug info
        self.printBoardArray()
        print("New game started! Player 1's turn (White).")

        # Redraw the board
        self.update()
