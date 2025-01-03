from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from board import Board
from score_board import ScoreBoard
from main_menu import Menu


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
        self.scoreBoard = ScoreBoard()
        self.board = Board(self, self.scoreBoard)

        # Add pages to stackedWidget
        self.stackedWidget.addWidget(self.Menu)
        self.stackedWidget.addWidget(self.board)

        # Connect signals
        self.Menu.newGameSignal.connect(self.startGame)

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
        self.board.start()
        self.scoreBoard.make_connection(self.board)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scoreBoard)
        print("Game started: Player 1 vs Player 2")


    def resetGame(self):
        """Reset the game."""
        self.board.resetGame()
        self.stackedWidget.setCurrentWidget(self.Menu)

    def endGame(self, winner):
        """Handle endgame."""
        winner_name = "Player 1" if winner == 1 else "Player 2"
        QMessageBox.information(self, "Game Over", f"{winner_name} wins the game!")
        self.resetGame()





