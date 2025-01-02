from PyQt6.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import pyqtSlot, pyqtSignal
import config


class Board(QWidget):
    '''Dummy Board class to define the required signals.'''

    # Define the missing signals
    clickLocationSignal = pyqtSignal(str)
    updateTimerSignal = pyqtSignal(int)
    updateScoreSignal = pyqtSignal(dict)
    updateTurnSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()


class ScoreBoard(QDockWidget):
    '''# base the score_board on a QDockWidget'''

    def __init__(self):
        super().__init__()
        self.initUI()

        # When config.turn = 0, it's up to the player 1 to play
        # When config.turn = 1, it's up to the player 2 to play
        config.turn = 0

    def initUI(self):
        '''initiates ScoreBoard UI'''
        self.resize(200, 200)
        self.setWindowTitle('ScoreBoard')

        # create a widget to hold other widgets
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()

        # create labels to display scores and turn
        self.label_player1Score = QLabel("Player 1 Score: 0")
        self.label_player2Score = QLabel("Player 2 Score: 0")
        self.label_turn = QLabel("Turn: Player 1")

        # create two labels which will be updated by signals
        self.label_clickLocation = QLabel("Click Location: ")
        self.label_timeRemaining = QLabel("Time remaining: ")

        self.mainWidget.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.label_player1Score)
        self.mainLayout.addWidget(self.label_player2Score)
        self.mainLayout.addWidget(self.label_turn)
        self.mainLayout.addWidget(self.label_clickLocation)
        self.mainLayout.addWidget(self.label_timeRemaining)
        self.setWidget(self.mainWidget)

    def make_connection(self, board):
        '''this handles a signal sent from the board class'''
        # when the clickLocationSignal is emitted in board the setClickLocation slot receives it
        board.clickLocationSignal.connect(self.setClickLocation)
        # when the updateTimerSignal is emitted in the board the setTimeRemaining slot receives it
        board.updateTimerSignal.connect(self.setTimeRemaining)
        # connect signals for updating scores and turn
        board.updateScoreSignal.connect(self.setScores)
        board.updateTurnSignal.connect(self.setTurn)

    @pyqtSlot(str)
    def setClickLocation(self, clickLoc):
        '''updates the label to show the click location'''
        self.label_clickLocation.setText("Click Location: " + clickLoc)
        print('slot ' + clickLoc)

    @pyqtSlot(int)
    def setTimeRemaining(self, timeRemaining):
        '''updates the time remaining label to show the time remaining'''
        update = "Time Remaining: " + str(timeRemaining)
        self.label_timeRemaining.setText(update)
        print('slot ' + str(timeRemaining))

    @pyqtSlot(dict)
    def setScores(self, scores):
        '''updates the scores for both players'''
        self.label_player1Score.setText(f"Player 1 Score: {scores.get('player1', 0)}")
        self.label_player2Score.setText(f"Player 2 Score: {scores.get('player2', 0)}")
        print('Updated scores: ', scores)

    @pyqtSlot(int)
    def setTurn(self, turn):
        '''updates the turn label to show which player's turn it is'''
        player = "Player 1" if turn == 0 else "Player 2"
        self.label_turn.setText(f"Turn: {player}")
        print('Updated turn: ', player)