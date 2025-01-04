from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from board import Board
from main_menu import Menu
from score_board import ScoreBoard
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
        self.board = None  # Initialize board later in startGame

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
        print("Starting the game...")
        if not self.board:
            print("Initializing Board and Game Logic...")
            self.board = Board(parent=self, logic=GoGame(7))  # Initialize 7x7 board logic
            self.scoreBoard.make_connection(self.board)  # Link the board to the ScoreBoard
            self.scoreBoard.passTurnSignal.connect(self.board.pass_turn)  # Handle turn passing
            self.scoreBoard.passTurnSignal.connect(self.scoreBoard.updateTurn)  # Update turn display

        self.stackedWidget.setCurrentWidget(self.scoreBoard)  # Switch to ScoreBoard
        self.board.start_game()  # Reset the board for a new game
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scoreBoard)
        print("Game started: Player 1 vs Player 2")

    def resetGame(self):
        """Reset the game."""
        print("Resetting the game...")
        if self.board:
            self.board.reset()  # Reset the board
        self.scoreBoard.resetGame()  # Reset the ScoreBoard
        self.stackedWidget.setCurrentWidget(self.Menu)  # Return to the menu
        print("Game reset and returned to the menu.")

    def endGame(self):
        """Handle the end-of-game scenario by calculating and displaying the scores."""
        print("Ending the game and calculating scores...")
        scores = self.board.logic.calculate_scores()  # Fetch final scores
        black_score = scores["black"]
        white_score = scores["white"]

        if black_score > white_score:
            winner_message = f"Black wins by {black_score - white_score} points!"
        elif white_score > black_score:
            winner_message = f"White wins by {white_score - black_score} points!"
        else:
            winner_message = "The game is a draw!"

        QMessageBox.information(self, "Game Over", winner_message)
        self.resetGame()  # Reset the game after displaying the result
