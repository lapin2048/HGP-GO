from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from board import Board
from main_menu import Menu
from score_board import ScoreBoard  # Ensure this is imported if used
from game_logic import GoGame

class Go(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initiates application UI"""
        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        # Initialize pages
        self.Menu = Menu()
        self.scoreBoard = ScoreBoard()  # Properly initialize ScoreBoard

        # Add Menu and ScoreBoard to stackedWidget
        self.stackedWidget.addWidget(self.Menu)
        self.stackedWidget.addWidget(self.scoreBoard)

        # Connect signals
        self.Menu.newGameSignal.connect(self.startGame)
        self.scoreBoard.resetGameSignal.connect(self.resetGame)  # Connect ScoreBoard reset signal

        # Window settings
        self.resize(800, 800)
        self.center()
        self.setWindowTitle("Go")
        self.show()

    def center(self):
        """Centers the window on the screen"""
        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def startGame(self):
        """Switch to the game view and start the game."""
        self.stackedWidget.setCurrentWidget(self.scoreBoard)  # Switch to ScoreBoard

        # Ensure the Board is initialized only in ScoreBoard
        if not hasattr(self.scoreBoard, "board_widget"):
            from board import Board
            from game_logic import GoGame
            self.scoreBoard.game_logic = GoGame(7)  # Initialize game logic
            self.scoreBoard.board_widget = Board(parent=self.scoreBoard, logic=self.scoreBoard.game_logic)
            self.scoreBoard.board_widget.setFixedSize(200, 200)
            self.scoreBoard.layout().addWidget(self.scoreBoard.board_widget)
            self.scoreBoard.layout().setAlignment(self.scoreBoard.board_widget, Qt.AlignmentFlag.AlignCenter)

        self.scoreBoard.board_widget.logic.reset_game()  # Reset the game logic
        print("Game started: Player 1 vs Player 2")


    def resetGame(self):
        """Reset the game to the initial state."""
        self.scoreBoard.resetGame()
        print("Game reset.")