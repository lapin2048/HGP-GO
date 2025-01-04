from piece import Piece
from copy import deepcopy
from PyQt6.QtWidgets import QMessageBox
class GoGame:
    def __init__(self, board_size, komi=6.5):
        """
        Initialize the game logic.
        :param board_size: The size of the Go board (e.g., 9 for a 9x9 board).
        :param komi: Compensation points for the white player.
        """
        self.board_size = board_size
        self.komi = komi
        self.reset_game()

    def reset_game(self):
        """
        Reset the game state and initialize the board.
        """
        self.board_state = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1  # Start with Black (1)
        self.pass_count = 0
        self.previous_states = []
        self.captured_stones = {1: 0, -1: 0}
        print("Game reset: Starting with White (-1)")  # Debug


    def get_board_snapshot(self):
        """
        Return a snapshot of the board state as a tuple for KO rule detection.
        """
        return tuple(tuple(row) for row in self.board_state)

    def place_stone(self, row, col):
        """
        Place a stone at (row, col) for the current player.
        :param row: Row index.
        :param col: Column index.
        :return: List of captured positions or None if the move is invalid.
        """
        if not self.is_valid_move(row, col):
            return None

        self.board_state[row][col] = self.current_player

        # Capture opponent stones
        captured_positions = self.capture_stones(row, col)

        # Check KO rule
        snapshot = self.get_board_snapshot()
        if snapshot in self.previous_states:
            self.board_state[row][col] = 0
            for r, c in captured_positions:
                self.board_state[r][c] = -self.current_player
            return None

        self.previous_states.append(snapshot)
        self.current_player *= -1  # Switch turns
        self.pass_count = 0
        return captured_positions

    def is_valid_move(self, row, col):
        """
        Check if a move is valid.
        :param row: Row index.
        :param col: Column index.
        :return: True if valid, False otherwise.
        """
        if not self.is_within_bounds(row, col) or self.board_state[row][col] != 0:
            return False

        self.board_state[row][col] = self.current_player
        if self.is_suicide(row, col):
            self.board_state[row][col] = 0
            return False

        self.board_state[row][col] = 0
        return True

    def is_suicide(self, row, col):
        """
        Check if placing a stone is a suicide move.
        :param row: Row index.
        :param col: Column index.
        :return: True if suicide, False otherwise.
        """
        visited = set()
        return self.count_liberties(row, col, visited) == 0
    
    def capture_stones(self, row, col):
        """
        Capture opponent stones with no liberties.
        :param row: Row index.
        :param col: Column index.
        :return: List of captured positions.
        """
        opponent = -self.current_player
        captured_positions = []

        for nr, nc in self.get_neighbors(row, col):
            if self.board_state[nr][nc] == opponent:
                visited = set()
                if self.count_liberties(nr, nc, visited) == 0:
                    for pr, pc in visited:
                        self.board_state[pr][pc] = 0  # Remove captured stone
                        captured_positions.append((pr, pc))
                    # Update captured stones count
                    self.captured_stones[self.current_player] += len(visited)
                    print(f"Captured stones updated: {self.captured_stones}")  # Debug

        return captured_positions


    def count_liberties(self, row, col, visited):
        """
        Count liberties for a group of stones.
        :param row: Row index.
        :param col: Column index.
        :param visited: Set of visited positions.
        :return: Number of liberties.
        """
        if (row, col) in visited:
            return 0

        visited.add((row, col))
        color = self.board_state[row][col]
        liberties = 0

        for nr, nc in self.get_neighbors(row, col):
            if self.board_state[nr][nc] == 0:
                liberties += 1
            elif self.board_state[nr][nc] == color:
                liberties += self.count_liberties(nr, nc, visited)

        return liberties

    def get_neighbors(self, row, col):
        """
        Get the neighbors of a position.
        :param row: Row index.
        :param col: Column index.
        :return: List of (row, col) neighbors.
        """
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, col))
        if row < self.board_size - 1:
            neighbors.append((row + 1, col))
        if col > 0:
            neighbors.append((row, col - 1))
        if col < self.board_size - 1:
            neighbors.append((row, col + 1))
        return neighbors

    def pass_turn(self):
        """
        Pass the current player's turn.
        """
        self.pass_count += 1
        self.current_player *= -1

    def is_game_over(self):
        """
        Check if the game is over (two consecutive passes).
        :return: True if game over, False otherwise.
        """
        return self.pass_count >= 2

    def calculate_scores(self):
        """
        Calculate the scores for both players.
        :return: Dictionary with scores for black and white.
        """
        print("Calculating scores...")  # Debug
        visited = set()
        territories = {1: 0, -1: 0}

        # Only calculate territory if moves have been made
        if any(any(cell != 0 for cell in row) for row in self.board_state):
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if (r, c) not in visited and self.board_state[r][c] == 0:
                        territory, owner = self.explore_territory(r, c, visited)
                        if owner:
                            territories[owner] += territory

        # Add captured stones and komi
        territories[1] += self.captured_stones.get(1, 0)  # Black's score
        territories[-1] += self.captured_stones.get(-1, 0) + self.komi  # White's score with komi

        print(f"Scores calculated: {territories}")  # Debug
        return {"black": territories[1], "white": territories[-1]}



    def explore_territory(self, row, col, visited):
        """
        Explore a territory and determine ownership.
        :param row: Row index.
        :param col: Column index.
        :param visited: Set of visited positions.
        :return: (size, owner) tuple.
        """
        stack = [(row, col)]
        territory = 0
        borders = set()

        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            if self.board_state[r][c] == 0:
                territory += 1
                stack.extend(self.get_neighbors(r, c))
            else:
                borders.add(self.board_state[r][c])

        owner = borders.pop() if len(borders) == 1 else 0
        return territory, owner
    
    def get_piece_at(self, row, col):
        """
        Get the state of the piece at a specific position.
        :param row: Row index.
        :param col: Column index.
        :return: The state of the piece (0 for empty, 1 for Black, -1 for White).
        """
        if self.is_within_bounds(row, col):
            return self.board_state[row][col]
        return None
    
    def is_within_bounds(self, row, col):
        """
        Check if a position is within the board boundaries.
        :param row: Row index.
        :param col: Column index.
        :return: True if within bounds, False otherwise.
        """
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def get_current_player(self):
        """
        Get the current player.
        :return: 1 for Black, -1 for White.
        """
        return self.current_player

    def pass_turn(self):
        """
        Pass the current player's turn. If both players pass consecutively, the game ends.
        """
        self.pass_count += 1
        if self.pass_count >= 2:  # Both players passed consecutively
            return True  # Signal that the game should end
        self.current_player *= -1  # Switch turns
        return False  # Game continues
