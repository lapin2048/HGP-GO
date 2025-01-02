from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
import config

class Board(QFrame):
    updateTimerSignal = pyqtSignal(int)  # signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new piece to add
    updateScoreSignal = pyqtSignal(dict)  # signal sent to update the score
    updateTurnSignal = pyqtSignal(int)  # signal sent to update the turn

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
        self.scores = {"player1": 0, "player2": 0}

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

    def updateScores(self, player):
        '''Update the scores based on captured pieces.'''
        if player == 1:
            self.scores["player1"] += 1
        elif player == 2:
            self.scores["player2"] += 1
        self.updateScoreSignal.emit(self.scores)

    def mousePosToColRow(self, event):
        '''convert the mouse click event to a row and column'''
        x, y = event.position().x(), event.position().y()  # Get the x and y position of the mouse click
        a = (x - self.squareWidth()) / self.squareWidth()  # Calculate fractional column index
        b = (y - self.squareHeight()) / self.squareHeight()  # Calculate fractional row index
        round_a, round_b = round(a), round(b)  # Round to the nearest integer
        # Ensure the rounded indices are within bounds
        if 0 <= round_a < self.boardWidth and 0 <= round_b < self.boardHeight:
            return round_b, round_a  # Return as (row, column)
        else:
            return None, None  # Return None if outside bounds
        
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
        if self.counter == 0:
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
        '''This event is automatically called when the mouse is pressed.'''
        x, y = event.position().x(), event.position().y()
        clickLoc = f"click location [{x}, {y}]"  # Log the click location
        print("mousePressEvent() - " + clickLoc)

        row, col = self.mousePosToColRow(event)

        if row is not None and col is not None:  # Ensure the click is within bounds
            print(f"Converted to board position: Row {row}, Column {col}")
            if abs((col - ((x - self.squareWidth()) / self.squareWidth()))) < 0.2 and \
            abs((row - ((y - self.squareHeight()) / self.squareHeight()))) < 0.2:
                self.tryMove(col, row)
            self.clickLocationSignal.emit(clickLoc)
        else:
            print("Clicked outside the board")

            
    def resetGame(self):
        '''clears pieces from the board'''
        self.boardArray = [[0 for _ in range(self.boardWidth + 1)] for _ in range(self.boardHeight + 1)]
        self.scores = {"player1": 0, "player2": 0}
        self.updateScoreSignal.emit(self.scores)

    def tryMove(self, newX, newY):
        '''tries to move a piece'''
        if self.boardArray[newY][newX] == 0: # If the intersection is empty
            newBoardPlanned = eval(str(self.boardArray)) # Create a deep copy
            newBoardPlanned[newY][newX] = config.turn + 1
            if not newBoardPlanned in self.history: # Eternity Rule
                print(True)
                if self.free(newBoardPlanned, newX, newY): # Suicide Rule
                    print(True)
                    self.boardArray = newBoardPlanned
                    self.repaint()
                    self.updateScores(config.turn + 1)
                    config.turn = 1 - config.turn
                    self.updateTurnSignal.emit(config.turn)
                    self.history.append(self.boardArray)
                else:
                    print(False)

    def capturable(self, boardArray, x, y, already_checked=[]):
        '''A method used for the free method.'''
        piece = boardArray[y][x] # Should be 1 or 2 depending on the piece
        w, h = len(boardArray[0]), len(boardArray)
        adjacentPositions = {}
        if x > 0:
            adjacentPositions[(x - 1, y)] = boardArray[y][x - 1]
        if x < w - 1:
            adjacentPositions[(x + 1, y)] = boardArray[y][x + 1]
        if y > 0:
            adjacentPositions[(x, y - 1)] = boardArray[y - 1][x]
        if y < h - 1:
            adjacentPositions[(x, y + 1)] = boardArray[y + 1][x]

        if 0 in adjacentPositions.values():
            return False

        for (i, j), value in adjacentPositions.items():
            if not (i, j) in already_checked:
                if value == piece and not self.capturable(boardArray, i, j, already_checked + [(x, y)]):
                    return False

        return True

    def free(self, boardArray, x, y, already_checked=[]):
        '''Returns True if the piece at (x, y) has at least one liberty
        and False otherwise.
        The already_checked argument includes positions already checked.'''
        piece = boardArray[y][x] # Should be 1 or 2 depending on the piece
        w, h = len(boardArray[0]), len(boardArray)
        adjacentPositions = {}
        if x > 0:
            adjacentPositions[(x - 1, y)] = boardArray[y][x - 1]
        if x < w - 1:
            adjacentPositions[(x + 1, y)] = boardArray[y][x + 1]
        if y > 0:
            adjacentPositions[(x, y - 1)] = boardArray[y - 1][x]
        if y < h - 1:
            adjacentPositions[(x, y + 1)] = boardArray[y + 1][x]

        if 0 in adjacentPositions.values():
            return True

        for (i, j), value in adjacentPositions.items():
            if value != piece and self.capturable(boardArray, i, j):
                return True

        for (i, j), value in adjacentPositions.items():
            if value == piece and not (i, j) in already_checked:
                if self.free(boardArray, i, j, already_checked + [(x, y)]):
                    return True

        return False

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
        squareWidth = self.squareWidth()
        squareHeight = self.squareHeight()
        for row in range(0, len(self.boardArray)):
            for col in range(0, len(self.boardArray[0])):
                square_content = self.boardArray[row][col]
                if square_content > 0:
                    painter.save()
                    painter.translate(col * squareWidth, row * squareHeight)

                    a = 255 * square_content - 255
                    painter.setBrush(QBrush(QColor(a, a, a)))

                    radius1 = round((self.squareWidth() - 2) / 2)
                    radius2 = round((self.squareHeight() - 2) / 2)
                    center = QPoint(radius1 + squareWidth // 2, radius2 + squareHeight // 2)
                    painter.drawEllipse(center, radius1, radius2)
                    painter.restore()
