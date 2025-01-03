class GoGame:
    print("Game Logic Object Created")

    def __init__(self, board_size):
        self.board_size = board_size
        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1  # 1 for Black, -1 for White
        self.pass_count = 0
        self.black_score = 0
        self.white_score = 0
        self.previous_states = []  # For KO rule prevention
        self.captured_stones = {"black": 0, "white": 0}

    def get_board_state_snapshot(self):
        return tuple(tuple(row) for row in self.board)

    def get_board_state(self):
        return {(r, c): self.board[r][c] for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] != 0}

    def place_stone(self, row, col):
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return None
        if self.board[row][col] != 0:
            return None

        self.board[row][col] = self.current_player
        if self.is_suicide(row, col):
            self.board[row][col] = 0
            return None

        captured_positions = self.capture_stones(row, col)

        snapshot = self.get_board_state_snapshot()
        if snapshot in self.previous_states:
            self.board[row][col] = 0
            for r, c in captured_positions:
                self.board[r][c] = -self.current_player
            return None

        self.previous_states.append(snapshot)
        self.pass_count = 0
        self.current_player = -self.current_player
        return captured_positions

    def capture_stones(self, boardArray, x, y):
        """Capture any opponent stones that have no liberties."""
        captured_positions = []
        opponent = 2 if boardArray[y][x] == 1 else 1
        w, h = len(boardArray[0]), len(boardArray)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and boardArray[ny][nx] == opponent:
                if self.capturable(boardArray, nx, ny):
                    # Remove all stones in the captured group
                    captured_positions.extend(self.remove_group(boardArray, nx, ny))

        return captured_positions
    
    def remove_group(self, boardArray, x, y):
        """Remove a group of stones and return their positions."""
        group = []
        stack = [(x, y)]
        piece = boardArray[y][x]

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) not in group:
                group.append((cx, cy))
                boardArray[cy][cx] = 0  # Remove stone

                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < len(boardArray[0]) and 0 <= ny < len(boardArray) and boardArray[ny][nx] == piece:
                        stack.append((nx, ny))

        return group



    def remove_group(self, row, col):
        group = self._get_group(row, col)
        for r, c in group:
            self.board[r][c] = 0
        self.captured_stones["black" if self.current_player == 1 else "white"] += len(group)
        return group

    def is_suicide(self, row, col):
        visited = set()
        return self.count_liberties(row, col, visited) == 0 and not any(
            self.board[r][c] == -self.current_player and self.count_liberties(r, c) == 0 for r, c in self.get_neighbors(row, col)
        )

    def count_liberties(self, row, col, visited=None):
        if visited is None:
            visited = set()
        if (row, col) in visited or not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return 0
        if self.board[row][col] == 0:
            return 1
        if self.board[row][col] != self.current_player:
            return 0

        visited.add((row, col))
        return sum(self.count_liberties(r, c, visited) for r, c in self.get_neighbors(row, col))

    def get_neighbors(self, row, col):
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
        self.pass_count += 1
        self.current_player = -self.current_player

    def is_game_over(self):
        return self.pass_count >= 2

    def undo_stone(self, row, col, color_of_move, captured_positions):
        self.board[row][col] = 0
        for r, c in captured_positions:
            self.board[r][c] = -color_of_move
        self.captured_stones["black" if color_of_move == 1 else "white"] -= len(captured_positions)
        self.current_player = color_of_move
        self.previous_states.pop()

    def calculate_territories(self):
        visited = set()
        territories = {'black': 0, 'white': 0}
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) not in visited and self.board[r][c] == 0:
                    territory, owner = self._explore_territory(r, c, visited)
                    if owner == 1:
                        territories['black'] += territory
                    elif owner == -1:
                        territories['white'] += territory
        return territories

    def _explore_territory(self, row, col, visited):
        queue = [(row, col)]
        territory = 0
        borders = set()
        while queue:
            r, c = queue.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            if self.board[r][c] == 0:
                territory += 1
                queue.extend(self.get_neighbors(r, c))
            else:
                borders.add(self.board[r][c])
        if len(borders) == 1:
            return territory, borders.pop()
        return territory, 0

    def get_current_player(self):
        return self.current_player

    def get_scores(self):
        territories = self.calculate_territories()
        return {
            'black': self.captured_stones['black'] + territories['black'],
            'white': self.captured_stones['white'] + territories['white']
        }

    def get_final_scores(self, territories):
        scores = self.get_scores()
        scores['white'] += 6.5  # Komi
        return scores
    def valid_position(self, row, col):
        """
        Check if the given position (row, col) is valid for placing a stone.
        :param row: The row index of the position.
        :param col: The column index of the position.
        :return: True if the position is valid, False otherwise.
        """
        # Check if the position is within board boundaries
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False

        # Check if the position is empty
        if self.board[row][col] != 0:
            return False

        # Temporarily place the stone to simulate the move
        self.board[row][col] = self.current_player

        # Check for suicide
        if self.is_suicide(row, col):
            self.board[row][col] = 0  # Revert the move
            return False

        # Check for Ko rule violation
        snapshot = self.get_board_state_snapshot()
        if snapshot in self.previous_states:
            self.board[row][col] = 0  # Revert the move
            return False

        # Revert the move as all checks passed
        self.board[row][col] = 0
        return True
        

    def place_piece(self, row, col, player):
        """
        Place a piece on the board at the specified position if the move is valid.
        :param row: The row index where the piece is placed.
        :param col: The column index where the piece is placed.
        :param player: The current player (1 for Black, -1 for White).
        :return: List of captured positions if the move is valid, or None if invalid.
        """
        # Check if the move is valid
        if not self.valid_position(row, col):
            print(f"Invalid move by Player {player} at ({row}, {col}).")
            return None

        # Place the piece
        self.board[row][col] = player

        # Capture opponent stones
        captured_positions = []
        for neighbor_row, neighbor_col in self.get_neighbors(row, col):
            if self.board[neighbor_row][neighbor_col] == -player:  # Opponent's stone
                if self.count_liberties(neighbor_row, neighbor_col) == 0:
                    captured_positions.extend(self.remove_group(neighbor_row, neighbor_col))

        # Check for Ko rule violation
        snapshot = self.get_board_state_snapshot()
        if snapshot in self.previous_states:
            print("Move violates the Ko rule. Reverting move.")
            # Undo the move
            self.board[row][col] = 0
            for r, c in captured_positions:
                self.board[r][c] = -player
            return None

        # Update game state
        self.previous_states.append(snapshot)
        self.pass_count = 0
        self.current_player = -player  # Switch to the other player

        # Return captured positions for further processing (e.g., score updates)
        return captured_positions

