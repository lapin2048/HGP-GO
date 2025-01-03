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
    restartGameSignal = pyqtSignal()  # Emitted to restart the game
    endGameSignal = pyqtSignal(int)  # Emitted to declare a winner (0 for draw, 1/2 for player)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.skip_count = 0  # Tracks consecutive skips
        self.last_skipper = None  # Tracks the last player who skipped
        self.connectedBoard = None  # Reference to the game board

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
        self.label_player1 = QLabel("Player 1: 0")
        self.label_player2 = QLabel("Player 2: 0")
        self.label_turn = QLabel("Turn: Player 1")
        self.label_capturedP1 = QLabel("Captured by P1: 0")
        self.label_capturedP2 = QLabel("Captured by P2: 0")
        self.label_territoryP1 = QLabel("Territory P1: 0")
        self.label_territoryP2 = QLabel("Territory P2: 0")

        # Add buttons
        self.button_pass = QPushButton("Pass Turn")
        self.button_restart = QPushButton("Restart Game")

        # Layout setup
        self.mainLayout.addWidget(self.label_clickLocation)
        self.mainLayout.addWidget(self.label_timeRemaining)

        playerLayout = QHBoxLayout()
        playerLayout.addWidget(self.label_player1)
        playerLayout.addWidget(self.label_player2)
        self.mainLayout.addLayout(playerLayout)

        capturedLayout = QHBoxLayout()
        capturedLayout.addWidget(self.label_capturedP1)
        capturedLayout.addWidget(self.label_capturedP2)
        self.mainLayout.addLayout(capturedLayout)

        territoryLayout = QHBoxLayout()
        territoryLayout.addWidget(self.label_territoryP1)
        territoryLayout.addWidget(self.label_territoryP2)
        self.mainLayout.addLayout(territoryLayout)

        self.mainLayout.addWidget(self.label_turn)
        self.mainLayout.addWidget(self.button_pass)
        self.mainLayout.addWidget(self.button_restart)

        self.mainWidget.setLayout(self.mainLayout)
        self.setWidget(self.mainWidget)

    def make_connection(self, board):
        """Connect signals from the board to the ScoreBoard."""
        self.connectedBoard = board
        board.clickLocationSignal.connect(self.setClickLocation)
        board.updateTimerSignal.connect(self.setTimeRemaining)
        self.button_pass.clicked.connect(self.skipTurn)
        self.button_restart.clicked.connect(self.restartGameSignal.emit)

    @pyqtSlot(str)
    def setClickLocation(self, clickLoc):
        """Update click location display."""
        self.label_clickLocation.setText("Click Location: " + clickLoc)

    @pyqtSlot(int)
    def setTimeRemaining(self, timeRemaining):
        """Update the timer label."""
        self.label_timeRemaining.setText(f"Time Remaining: {timeRemaining}s")

    def updateScores(self, p1_score, p2_score):
        """Update player scores."""
        self.label_player1.setText(f"Player 1: {p1_score}")
        self.label_player2.setText(f"Player 2: {p2_score}")

    def updateCapturedStones(self, captured_p1, captured_p2):
        """Update captured stones count."""
        self.label_capturedP1.setText(f"Captured by P1: {captured_p1}")
        self.label_capturedP2.setText(f"Captured by P2: {captured_p2}")

    def updateTerritory(self, territory_p1, territory_p2):
        """Update territory information."""
        self.label_territoryP1.setText(f"Territory P1: {territory_p1}")
        self.label_territoryP2.setText(f"Territory P2: {territory_p2}")

    def updateTurn(self, current_turn):
        """Update the turn display."""
        player = "Player 1" if current_turn == 1 else "Player 2"
        color = "White" if current_turn == 1 else "Black"
        self.label_turn.setText(f"Turn: {player} ({color})")

    def skipTurn(self):
        """Handle player skipping their turn."""
        if not self.connectedBoard:
            return

        current_player = self.connectedBoard.player_turn

        # Update skip tracking
        if self.last_skipper is None or self.last_skipper != current_player:
            self.last_skipper = current_player
            self.skip_count = 1
        else:
            self.skip_count += 1

        # Check end game conditions
        if self.skip_count >= 2:  # Consecutive skips
            self.endGameSignal.emit(0)  # Emit a draw signal
        elif self.skip_count >= 3:
            self.endGameSignal.emit(3 - current_player)  # Opponent wins

        # Emit signal for skipping turn
        self.passTurnSignal.emit()

    def resetSkipTracking(self):
        """Reset skip tracking."""
        self.skip_count = 0
        self.last_skipper = None

    def updateTurn(self, current_turn):
        """Update the turn label."""
        player = "Player 1" if current_turn == 1 else "Player 2"
        color = "White" if current_turn == 1 else "Black"
        self.label_turn.setText(f"Turn: {player} ({color})")

    def updatePrisoners(self, prisoners_p1, prisoners_p2):
        """Update captured stones for both players."""
        self.label_capturedP1.setText(f"Captured by P1: {prisoners_p1}")
        self.label_capturedP2.setText(f"Captured by P2: {prisoners_p2}")

    def updateTerritory(self, territory_p1, territory_p2):
        """Update territory for both players."""
        self.label_territoryP1.setText(f"Territory P1: {territory_p1}")
        self.label_territoryP2.setText(f"Territory P2: {territory_p2}")
