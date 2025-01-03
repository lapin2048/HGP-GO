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
        self.board = Board(self, GoGame(9))  # Pass ScoreBoard to Board

        # Add pages to stackedWidget
        self.stackedWidget.addWidget(self.Menu)
        self.stackedWidget.addWidget(self.board)

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
        """Switch to the game board and start the game."""
        self.stackedWidget.setCurrentWidget(self.board)
        self.board.start_game()  # Ensure the board is reset for the new game
        self.scoreBoard.make_connection(self.board)  # Link the board to the ScoreBoard
        self.scoreBoard.passTurnSignal.connect(self.board.pass_turn)  # Handle turn passing
        self.scoreBoard.passTurnSignal.connect(self.scoreBoard.updateTurn)  # Update turn display
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scoreBoard)
        print("Game started: Player 1 vs Player 2")

    def resetGame(self):
        """Reset the game."""
        self.board.reset()  # Reset the board state
        self.stackedWidget.setCurrentWidget(self.Menu)  # Go back to the menu
    
    def endGame(self):
        """Handle the end-of-game scenario by calculating and displaying the scores."""
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


    def resetGame(self):
        """Reset the game."""
        print("Resetting the game...")  # Debug statement
        self.board.reset()  # Reset the board
        self.scoreBoard.resetGame()  # Reset the ScoreBoard
