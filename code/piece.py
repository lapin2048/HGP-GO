class Piece:
    def __init__(self, row, col, color):
        """
        Initialize a piece with its position and color.
        :param row: Row position of the piece.
        :param col: Column position of the piece.
        :param color: 1 for Black, -1 for White, 0 for empty.
        """
        self.row = row
        self.col = col
        self.color = color
        self.captured = False

    def capture(self):
        """
        Mark the piece as captured.
        """
        self.captured = True

    def release(self):
        """
        Unmark the piece as captured.
        """
        self.captured = False

    def __str__(self):
        """
        String representation of the piece for debugging.
        """
        return f"Piece(row={self.row}, col={self.col}, color={'Black' if self.color == 1 else 'White' if self.color == -1 else 'Empty'})"

    def __repr__(self):
        return self.__str__()