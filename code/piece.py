class Piece:
    """
    Piece implementation for a Go game.
    No piece state = 0
    White piece state = 1
    Black piece state = 2
    """

    def __init__(self, state: int, row: int | None = None, col: int | None = None):
        """
        Initialize a piece with its state and position.
        :param state: 0 for empty, 1 for White, 2 for Black.
        :param row: The row position of the piece.
        :param col: The column position of the piece.
        """
        self.state = state
        self.position = (row, col)
        self.__all_states = {0: "No Piece", 1: "White", 2: "Black"}
        self.name = self.__all_states[self.state]

    def change_state(self, new_state: int):
        """
        Change the state of the piece.
        :param new_state: The new state for the piece.
        """
        if new_state != self.state:
            self.state = new_state
            self.name = self.__all_states[self.state]
        else:
            raise ValueError(
                f"Cannot change piece at {self.position} to the same state ({self.__all_states[new_state]})."
            )

    def __str__(self):
        """String representation of the piece for debugging."""
        return f"{self.name} at {self.position}"

    def __repr__(self):
        return self.__str__()
