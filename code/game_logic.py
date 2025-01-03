from piece import Piece
from copy import deepcopy
from PyQt6.QtWidgets import QMessageBox
class GoGame:
    def __init__(self, board, board_size, komi=6.5):
        """
        Initialize the game logic.
        :param board_size: The size of the Go board (e.g., 9 for a 9x9 board).
        :param komi: Compensation points for the white player.
        """
        self.board = board
        self.board_size = board_size
        self.komi = komi
        self.reset_game()

    def reset_game(self):
        """
        Reset the game state and initialize the board.
        """
        print("Game Reset", self.board_size)
        self.board = [[Piece(0, row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        self.current_player = 1  # 1 for Black, 2 for White
        self.previous_states = []  # Keep track of previous board states for Ko rule
        self.captured_stones = {1: 0, 2: 0}  # Track captured stones for each player
        self.pass_count = 0
        self.game_active = True

    def place_stone(self, row, col):
        """
        Place a stone on the board if the move is valid.
        :param row: Row index.
        :param col: Column index.
        :return: List of captured positions or None if the move is invalid.
        """
        if not self.is_valid_move(row, col):
            return None

        self.board[row][col].state = self.current_player
        captured_positions = self.capture_stones(row, col)

        # Check Ko rule
        board_snapshot = self.get_board_snapshot()
        if board_snapshot in self.previous_states:
            self.board[row][col].state = 0
            for r, c in captured_positions:
                self.board[r][c].state = 3 - self.current_player
            return None

        self.previous_states.append(board_snapshot)
        self.current_player = 3 - self.current_player  # Switch turns
        self.pass_count = 0
        return captured_positions
    

    def is_valid_move(self, row, col):
        if not self.is_within_bounds(row, col) or self.board[row][col].state != 0:
            print(f"Move at ({row}, {col}) is out of bounds or the cell is occupied.")
            return False

        # Simuler le placement pour vérifier les règles
        self.board[row][col].state = self.current_player

        # Vérification des libertés (non-suicide)
        if self.is_suicide(row, col):
            print(f"Move at ({row}, {col}) is suicidal.")
            self.board[row][col].state = 0
            return False

        # Vérification de la règle de Ko
        snapshot = self.get_board_snapshot()
        if snapshot in self.previous_states:
            print(f"Move at ({row}, {col}) violates Ko rule.")
            self.board[row][col].state = 0
            return False

        self.board[row][col].state = 0
        return True

    def is_suicide(self, row, col):
        """
        Determine if placing a stone results in a suicidal move.
        :param row: Row index.
        :param col: Column index.
        :return: True if the move is suicidal, False otherwise.
        """
        visited = set()
        return self.count_liberties(row, col, visited) == 0

    def capture_stones(self, row, col):
        """
        Capture opponent stones if they have no liberties.
        :param row: Row index of the placed stone.
        :param col: Column index of the placed stone.
        :return: List of captured positions.
        """
        opponent = 3 - self.current_player
        captured_positions = []

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = row + dx, col + dy
            if self.is_within_bounds(nx, ny) and self.board[nx][ny].state == opponent:
                if self.is_group_captured(nx, ny):
                    captured_positions.extend(self.remove_group(nx, ny))

        if captured_positions:
            print(f"Captured stones at: {captured_positions}")
        return captured_positions

    def is_within_bounds(self, row, col):
        """
        Check if a position is within the board boundaries.
        :param row: Row index.
        :param col: Column index.
        :return: True if within bounds, False otherwise.
        """
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def is_group_captured(self, row, col):
        """
        Check if a group of stones is captured.
        :param row: Row index.
        :param col: Column index.
        :return: True if the group is captured, False otherwise.
        """
        visited = set()
        return self.count_liberties(row, col, visited) == 0

    def count_liberties(self, row, col, visited):
        """
        Count the liberties of a group of stones.
        :param row: Row index.
        :param col: Column index.
        :param visited: Set of visited positions.
        :return: Number of liberties.
        """
        if (row, col) in visited:
            return 0
        if not self.is_within_bounds(row, col):
            return 0
        if self.board[row][col].state == 0:
            return 1
        if self.board[row][col].state != self.current_player:
            return 0

        visited.add((row, col))
        liberties = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            liberties += self.count_liberties(row + dx, col + dy, visited)
        return liberties

    def remove_group(self, row, col):
        """
        Remove a group of stones from the board.
        :param row: Row index.
        :param col: Column index.
        :return: List of removed stone positions.
        """
        stack = [(row, col)]
        player = self.board[row][col].state
        captured = []

        while stack:
            x, y = stack.pop()
            if (x, y) in captured:
                continue
            captured.append((x, y))
            self.board[x][y].state = 0

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.is_within_bounds(nx, ny) and self.board[nx][ny].state == player:
                    stack.append((nx, ny))

        self.captured_stones[3 - player] += len(captured)
        return captured

    def get_board_snapshot(self):
        """
        Get a snapshot of the board state for Ko rule.
        :return: Tuple representation of the board state.
        """
        return tuple(tuple(piece.state for piece in row) for row in self.board)

    def pass_turn(self):
        """
        Pass the current player's turn.
        If both players pass consecutively, the game ends.
        """
        self.pass_count += 1
        if self.pass_count >= 2:
            self.end_game()
        else:
            self.current_player = 3 - self.current_player

    def end_game(self):
        """
        End the game and calculate the final scores.
        """
        self.game_active = False
        scores = self.calculate_scores()
        print(f"Game Over: Black - {scores['black']}, White - {scores['white']}")

    def calculate_scores(self):
        """
        Calculate the final scores for both players.
        :return: Dictionary with scores for Black and White.
        """
        visited = set()
        territories = {1: 0, 2: 0}

        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row, col) not in visited and self.board[row][col].state == 0:
                    territory, owner = self.explore_territory(row, col, visited)
                    if owner:
                        territories[owner] += territory

        territories[1] += self.captured_stones[1]
        territories[2] += self.captured_stones[2] + self.komi
        return {"black": territories[1], "white": territories[2]}

    def explore_territory(self, row, col, visited):
        """
        Explore a territory to determine its owner.
        :param row: Row index.
        :param col: Column index.
        :param visited: Set of visited positions.
        :return: Tuple containing the size of the territory and its owner.
        """
        stack = [(row, col)]
        territory = 0
        borders = set()

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))

            if self.board[x][y].state == 0:
                territory += 1
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if self.is_within_bounds(nx, ny):
                        stack.append((nx, ny))
            else:
                borders.add(self.board[x][y].state)

        owner = borders.pop() if len(borders) == 1 else 0
        return territory, owner

    def execute_move(self, row, col, player):
        """
        Execute a move on the board.
        :param row: Row index.
        :param col: Column index.
        :param player: The player making the move.
        :return: List of captured positions or None if the move is invalid.
        """
        print(f"Executing move at ({row}, {col}) for player {player}")
        return self.place_stone(row, col)
