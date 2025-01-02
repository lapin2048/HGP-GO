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

    def capture_stones(self, row, col):
        captured_positions = []
        opponent = -self.current_player
        for r, c in self.get_neighbors(row, col):
            if self.board[r][c] == opponent and self.count_liberties(r, c) == 0:
                captured_positions.extend(self.remove_group(r, c))
        return captured_positions

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
