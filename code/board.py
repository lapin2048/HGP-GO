from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
import config


class Board(QFrame):  # base the board on a QFrame widget
    updateTimerSignal = pyqtSignal(int)  # signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new piece to add

    boardWidth = 7
    boardHeight = 7
    timerSpeed = 1000  # the timer updates every 1 second
    counter = 30  # the number the counter will count down from

    def __init__(self, parent):
        super().__init__(parent)
        self.initBoard()
        # History of positions (the initial position with no pieces is not
        # recorded because there would be no risk of returning to an empty board)
        self.history = []

    def initBoard(self):
        '''initiates board'''
        self.timer = QTimer(self)  # create a timer for the game
        self.timer.timeout.connect(self.timerEvent)  # connect timeout signal to timerEvent method
        self.isStarted = False  # game is not currently started
        self.start()  # start the game which will start the timer

        # 0 represents no piece
        # 1 represents a piece of the player 1
        # 2 represents a piece of the player 2
        self.boardArray = [[0 for _ in range(self.boardWidth + 1)] for _ in range(self.boardHeight + 1)]
        self.printBoardArray()

    def printBoardArray(self):
        '''prints the boardArray in an attractive way'''
        print("boardArray:")
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.boardArray]))

    def mousePosToColRow(self, event):
        '''convert the mouse click event to a row and column'''
        pass  # Implement this method according to your logic

    def squareWidth(self):
        '''returns the width of one square in the board'''
        return round(self.contentsRect().width() / (self.boardWidth + 2))

    def squareHeight(self):
        '''returns the height of one square of the board'''
        return round(self.contentsRect().height() / (self.boardHeight + 2))

    def start(self):
        '''starts game'''
        self.isStarted = True  # set the boolean which determines if the game has started to TRUE
        self.resetGame()  # reset the game
        self.timer.start(self.timerSpeed)  # start the timer with the correct speed
        print("start () - timer is started")

    def timerEvent(self):
        '''this event is automatically called when the timer is updated. based on the timerSpeed variable '''
        # TODO adapt this code to handle your timers
        if Board.counter == 0:
            print("Game over")
        self.counter -= 1
        print('timerEvent()', self.counter)
        self.updateTimerSignal.emit(self.counter)

    def paintEvent(self, event):
        '''paints the board and the pieces of the game'''
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.black, 3, Qt.PenStyle.SolidLine))
        self.drawBoardSquares(painter)
        self.drawPieces(painter)

    def mousePressEvent(self, event):
        '''this event is automatically called when the mouse is pressed'''
        x, y = event.position().x(), event.position().y()
        clickLoc = "click location [" + str(x) + "," + str(y) + "]"  # the location where a mouse click was registered
        print("mousePressEvent() - " + clickLoc)
        a = (x - self.squareWidth()) / self.squareWidth()
        b = (y - self.squareHeight()) / self.squareHeight()
        round_a, round_b = round(a), round(b)
        print(abs(round_a - a), abs(round_b - b), self.boardArray[round_b][round_a])
        if abs(round_a - a) < 0.2 and abs(round_b - b) < 0.2:
            self.tryMove(round_a, round_b)
        self.clickLocationSignal.emit(clickLoc)

    def resetGame(self):
        '''clears pieces from the board'''
        # TODO write code to reset game

    def tryMove(self, newX, newY):
        '''tries to move a piece'''
        if self.boardArray[newY][newX] == 0: # If the intersection is empty
            newBoardPlanned = eval(str(self.boardArray)) # Create a deep copy
            newBoardPlanned[newY][newX] = config.turn + 1
            if not newBoardPlanned in self.history:
                self.boardArray = newBoardPlanned
                self.repaint()
                # The current player has played so we move on to the next turn
                config.turn = 1 - config.turn
                self.history.append(self.boardArray)

    def drawBoardSquares(self, painter):
        '''draw all the square on the board'''
        squareWidth = self.squareWidth()
        squareHeight = self.squareHeight()
        painter.setBrush(QBrush(QColor(120, 70, 20)))  # Set brush color
        painter.drawRect(0, 0, self.contentsRect().width(), self.contentsRect().height())
        for row in range(0, Board.boardHeight):
            for col in range(0, Board.boardWidth):
                painter.save()
                painter.translate(col * squareWidth, row * squareHeight)
                painter.drawRect(squareWidth, squareHeight, squareWidth, squareHeight)  # Draw rectangles
                painter.restore()

    def drawPieces(self, painter):
        '''draw the pieces on the board'''
        # We define squareWidth and squareHeight once and for all to avoid having
        # to compute it every time
        squareWidth = self.squareWidth()
        squareHeight = self.squareHeight()
        for row in range(0, len(self.boardArray)):
            for col in range(0, len(self.boardArray[0])):
                # If there is a piece to display
                square_content = self.boardArray[row][col]
                if square_content > 0:
                    painter.save()
                    painter.translate(col * squareWidth, row * squareHeight)

                    # The piece color depends on the player who owns it
                    a = 255 * square_content - 255
                    painter.setBrush(QBrush(QColor(a, a, a)))

                    radius1 = round((self.squareWidth() - 2) / 2)
                    radius2 = round((self.squareHeight() - 2) / 2)
                    center = QPoint(radius1 + squareWidth // 2, radius2 + squareHeight // 2)
                    painter.drawEllipse(center, radius1, radius2)
                    painter.restore()
