from PyQt6.QtWidgets import (
    QDockWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot


class ScoreBoard(QDockWidget):
    """ScoreBoard for managing game state and UI."""

    passTurnSignal = pyqtSignal()  # Emitted when a player passes their turn
    resetGameSignal = pyqtSignal()  # Emitted to restart the game
    endGameSignal = pyqtSignal(int)  # Emitted to declare a winner (0 for draw, 1/2 for player)

    def __init__(self):
        super().__init__()
        self.init_backend()
        self.initUI()
        self.connectedBoard = None  # Reference to the game board

    def init_backend(self):
        """Initialize backend score tracking fields."""
        self.black_score = 0
        self.white_score = 0
        self.captured_black = 0  # Stones captured by White
        self.captured_white = 0  # Stones captured by Black
        self.territories = {"black": 0, "white": 0}

    def initUI(self):
        """Initialize ScoreBoard UI."""
        self.resize(300, 400)
        self.setWindowTitle("ScoreBoard")

        # Create main widget and layout
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()

        # Add labels
        self.label_clickLocation = QLabel("Click Location: ")
        self.label_timeRemaining = QLabel("Time Remaining: ")
        self.label_blackScore = QLabel("Black Score: 0")
        self.label_whiteScore = QLabel("White Score: 0")
        self.label_turn = QLabel("Turn: Black")
        self.label_capturedBlack = QLabel("Captured Black: 0")
        self.label_capturedWhite = QLabel("Captured White: 0")
        self.label_territoryBlack = QLabel("Territory Black: 0")
        self.label_territoryWhite = QLabel("Territory White: 0")

        # Add buttons
        self.button_pass = QPushButton("Pass Turn")
        self.button_restart = QPushButton("Restart Game")

        # Layout setup
        self.mainLayout.addWidget(self.label_clickLocation)
        self.mainLayout.addWidget(self.label_timeRemaining)

        playerLayout = QHBoxLayout()
        playerLayout.addWidget(self.label_blackScore)
        playerLayout.addWidget(self.label_whiteScore)
        self.mainLayout.addLayout(playerLayout)

        capturedLayout = QHBoxLayout()
        capturedLayout.addWidget(self.label_capturedBlack)
        capturedLayout.addWidget(self.label_capturedWhite)
        self.mainLayout.addLayout(capturedLayout)

        territoryLayout = QHBoxLayout()
        territoryLayout.addWidget(self.label_territoryBlack)
        territoryLayout.addWidget(self.label_territoryWhite)
        self.mainLayout.addLayout(territoryLayout)

        self.mainLayout.addWidget(self.label_turn)
        self.mainLayout.addWidget(self.button_pass)
        self.mainLayout.addWidget(self.button_restart)

        self.mainWidget.setLayout(self.mainLayout)
        self.setWidget(self.mainWidget)

    def make_connection(self, board):
        """Connect signals from the board to the ScoreBoard."""
        if not board:
            raise ValueError("Invalid board instance provided for connection.")

        self.connectedBoard = board
        board.positionClicked.connect(self.setClickLocation)
        board.updateTimerSignal.connect(self.setTimeRemaining)
        self.button_pass.clicked.connect(self.skipTurn)
        self.button_restart.clicked.connect(self.resetGameSignal.emit)

    @pyqtSlot(str)
    def setClickLocation(self, clickLoc):
        """Update click location display."""
        self.label_clickLocation.setText("Click Location: " + clickLoc)

    @pyqtSlot(int)
    def setTimeRemaining(self, timeRemaining):
        """Update the timer label."""
        self.label_timeRemaining.setText(f"Time Remaining: {timeRemaining}s")

    def add_score(self, player, points):
        """Add points to a player's score (1=Black, -1=White)."""
        if player == 1:
            self.black_score += points
        else:
            self.white_score += points
        self.updateScores()

    def add_captured_stone(self, player):
        """Increment the count of stones captured by the opponent."""
        if player == 1:
            self.captured_white += 1
        else:
            self.captured_black += 1
        self.updateScores()

    def update_territory(self, player, points):
        """Update the territory count for a player (1=Black, -1=White)."""
        if player == 1:
            self.territories["black"] += points
        else:
            self.territories["white"] += points
        self.updateScores()

    def calculate_final_score(self, komi=6.5):
        """Calculate the final score including captured stones and territory."""
        final_black_score = self.black_score + self.captured_black + self.territories["black"]
        final_white_score = self.white_score + self.captured_white + self.territories["white"] + komi
        return {"black": final_black_score, "white": final_white_score}

    def resetGame(self):
        """Reset all scores and update the UI."""
        self.init_backend()
        self.updateScores()
        self.label_turn.setText("Turn: Black")
        self.label_timeRemaining.setText("Time Remaining: ")
        self.label_clickLocation.setText("Click Location: ")

    def updateScores(self):
        """Update the UI with the current scores."""
        self.label_blackScore.setText(f"Black Score: {self.black_score}")
        self.label_whiteScore.setText(f"White Score: {self.white_score}")
        self.label_capturedBlack.setText(f"Captured Black: {self.captured_black}")
        self.label_capturedWhite.setText(f"Captured White: {self.captured_white}")
        self.label_territoryBlack.setText(f"Territory Black: {self.territories['black']}")
        self.label_territoryWhite.setText(f"Territory White: {self.territories['white']}")

    def updateTurn(self, current_turn):
        """Update the turn label."""
        player = "Black" if current_turn == 1 else "White"
        self.label_turn.setText(f"Turn: {player}")

    def skipTurn(self):
        """Handle the pass turn action."""
        self.passTurnSignal.emit()
        self.updateTurn(self.connectedBoard.logic.current_player)
