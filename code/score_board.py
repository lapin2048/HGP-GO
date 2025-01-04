from PyQt6.QtWidgets import (
    QDockWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QGridLayout,
)
from board import Board
from game_logic import GoGame
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtWidgets import QDockWidget, QVBoxLayout, QLabel, QWidget, QSpacerItem, QSizePolicy, QPushButton, QHBoxLayout


class ScoreBoard(QDockWidget):
    """ScoreBoard for managing game state and UI."""

    passTurnSignal = pyqtSignal()  # Emitted when a player passes their turn
    resetGameSignal = pyqtSignal()  # Emitted to restart the game
    endGameSignal = pyqtSignal(int)  # Emitted to declare a winner (0 for draw, 1/2 for player)
    
    def __init__(self):
        super().__init__()
        self.board_widget = None  # Placeholder for the external Board instance
        self.init_backend()
        self.initUI()
    
    def init_backend(self):
        """Initialize game logic."""
        from game_logic import GoGame
        self.game_logic = GoGame(8)  # Initialize game logic with a 7x7 board

    def initUI(self):
        """Initialize ScoreBoard UI."""
        self.setWindowTitle("ScoreBoard")

        # Disable undocking
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        # Main vertical layout
        self.mainLayout = QVBoxLayout()  # Define mainLayout as an instance attribute

        # Add labels for stats (top row)
        statsLayout = QHBoxLayout()
        self.label_blackScore = QLabel("Black Score: 0")
        self.label_whiteScore = QLabel("White Score: 0")
        self.label_timeRemaining = QLabel("Time Remaining: ")
        statsLayout.addWidget(self.label_blackScore, alignment=Qt.AlignmentFlag.AlignLeft)
        statsLayout.addWidget(self.label_timeRemaining, alignment=Qt.AlignmentFlag.AlignCenter)
        statsLayout.addWidget(self.label_whiteScore, alignment=Qt.AlignmentFlag.AlignRight)
        self.mainLayout.addLayout(statsLayout)

        # Add label for click location
        self.label_clickLocation = QLabel("Click Location: ")  # Add label for click location
        self.mainLayout.addWidget(self.label_clickLocation)

        # Add current turn label
        self.label_turn = QLabel("Turn: White")  # Add label for player turn
        self.label_turn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.label_turn)

        # Add vertical spacer above the board
        self.mainLayout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # Buttons for actions (bottom row)
        buttonLayout = QHBoxLayout()
        self.button_pass = QPushButton("Pass Turn")
        self.button_restart = QPushButton("Restart Game")
        buttonLayout.addWidget(self.button_pass)
        buttonLayout.addWidget(self.button_restart)
        self.mainLayout.addLayout(buttonLayout)

        # Set the layout
        centralWidget = QWidget()
        centralWidget.setLayout(self.mainLayout)
        self.setWidget(centralWidget)


    def set_board(self, board):
        """Set the external Board instance to display in the ScoreBoard."""
        if self.board_widget is not None:
            self.boardLayout.removeWidget(self.board_widget)  # Remove the old board if it exists
            self.board_widget.setParent(None)

        self.board_widget = board
        self.boardLayout.addWidget(self.board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def make_connection(self, board):
        """Connect signals from the board to the ScoreBoard."""
        if not board:
            raise ValueError("Invalid board instance provided for connection.")
        self.connectedBoard = board
        print("Connecting signals...")

        # Connect signals
        board.positionClicked.connect(self.setClickLocation)
        print("Connected: positionClicked -> setClickLocation")

        board.updateTimerSignal.connect(self.setTimeRemaining)
        print("Connected: updateTimerSignal -> setTimeRemaining")

        self.button_pass.clicked.connect(self.skipTurn)
        print("Connected: button_pass -> skipTurn")

        self.button_restart.clicked.connect(lambda: self.resetGameSignal.emit())
        print("Connected: button_restart -> resetGameSignal")

        board.updateScoresSignal.connect(self.updateScores)
        print("Connected: updateScoresSignal -> updateScores")
        board.updateCapturedStonesSignal.connect(self.updateCapturedStones)

    @pyqtSlot(str)
    def setClickLocation(self, clickLoc):
        """Update click location display."""
        print(f"Click Location: {clickLoc}")  # Debug
        self.label_clickLocation.setText("Click Location: " + clickLoc)

    @pyqtSlot(int)
    def setTimeRemaining(self, timeRemaining):
        """Update the timer label."""
        print(f"Time Remaining: {timeRemaining}s")  # Debug
        self.label_timeRemaining.setText(f"Time Remaining: {timeRemaining}s")

    def updateScores(self, scores):
        print(f"Scores updated in UI: {scores}")  # Debug
        if not scores:
            scores = {'black': 0, 'white': 0}  # Ensure scores dictionary exists
        self.label_blackScore.setText(f"Black Score: {scores['black']}")
        self.label_whiteScore.setText(f"White Score: {scores['white']}")
        self.updateTurn()

    def updateCapturedStones(self, captured_black, captured_white):
        """Update the captured stones in the UI."""
        print(f"Captured Stones updated: Black - {captured_black}, White - {captured_white}")  # Debug

    def updateTurn(self):
        """Update the turn label based on the current player."""
        if self.connectedBoard:  # Ensure the board is connected
            current_player = self.connectedBoard.logic.get_current_player()
            player = "Black" if current_player == 1 else "White"
            self.label_turn.setText(f"Turn: {player}")

    def skipTurn(self):
        """Handle the pass turn action."""
        print("Turn skipped.")  # Debug
        self.passTurnSignal.emit()  # Emit the signal to pass the turn
        self.updateTurn()

    def resetGame(self):
        """Reset all scores and update the UI."""
        print("Resetting ScoreBoard...")  # Debug
        self.init_backend()
        self.label_blackScore.setText("Black Score: 0")
        self.label_whiteScore.setText("White Score: 0")
        self.label_turn.setText("Turn: White")
        self.label_timeRemaining.setText("Time Remaining: ")