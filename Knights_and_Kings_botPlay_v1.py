import random

BOARD_SIZE = 5
EMPTY = '.'
FILES = ['a', 'b', 'c', 'd', 'e']
RANKS = ['5', '4', '3', '2', '1']

PIECES = {
    'player': {'king': '♔', 'knight': '♘'},
    'ai': {'king': '♚', 'knight': '♞'}
}

class MiniChess:
    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.player_pieces = {'king': (4, 2), 'knight': (4, 3)}
        self.ai_pieces = {'king': (0, 2), 'knight': (0, 1)}
        self.move_log = []
        self.turn = 'player'
        self.place_pieces()

    def place_pieces(self):
        for name, (x, y) in self.player_pieces.items():
            self.board[x][y] = PIECES['player'][name]
        for name, (x, y) in self.ai_pieces.items():
            self.board[x][y] = PIECES['ai'][name]

    def display_board(self):
        print("    " + " ".join(FILES))
        for i in range(BOARD_SIZE):
            print(f"{RANKS[i]} | {' '.join(self.board[i])}")
        print()

    def indices_to_algebraic(self, x, y):
        return FILES[y] + RANKS[x]

    def log_move(self, piece, x, y, is_player):
        symbol = 'K' if piece == 'king' else 'N'
        prefix = '' if is_player else '... '
        self.move_log.append(f"{prefix}{symbol}{self.indices_to_algebraic(x, y)}")

    def is_attacked_by_knight(self, x, y, opponent):
        for name, (ox, oy) in opponent.items():
            if name == 'knight' and (abs(ox - x), abs(oy - y)) in [(1, 2), (2, 1)]:
                return True
        return False

    def in_check(self, is_player):
        king_pos = (self.player_pieces if is_player else self.ai_pieces).get('king')
        if not king_pos:
            return False
        opponent = self.ai_pieces if is_player else self.player_pieces
        return self.is_attacked_by_knight(*king_pos, opponent)

    def exposes_king(self, piece, x, y, nx, ny, is_player):
        team = self.player_pieces if is_player else self.ai_pieces
        opponent = self.ai_pieces if is_player else self.player_pieces
        snapshot = [row[:] for row in self.board]
        captured = None

        for op, pos in list(opponent.items()):
            if pos == (nx, ny):
                captured = op
                del opponent[op]
                break

        self.board[x][y] = EMPTY
        self.board[nx][ny] = PIECES['player' if is_player else 'ai'][piece]
        team[piece] = (nx, ny)

        in_danger = self.in_check(is_player)

        team[piece] = (x, y)
        if captured:
            opponent[captured] = (nx, ny)
        self.board = [row[:] for row in snapshot]

        return in_danger

    def valid_move(self, piece, x, y, nx, ny, is_player):
        if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE):
            return False
        team_syms = PIECES['player' if is_player else 'ai'].values()
        if self.board[nx][ny] in team_syms:
            return False
        dx, dy = abs(nx - x), abs(ny - y)

        if piece == 'knight' and (dx, dy) not in [(2, 1), (1, 2)]:
            return False

        if piece == 'king':
            if dx > 1 or dy > 1:
                return False
            opponent_king = (self.ai_pieces if is_player else self.player_pieces).get('king')
            if opponent_king and abs(opponent_king[0] - nx) <= 1 and abs(opponent_king[1] - ny) <= 1:
                return False

        return not self.exposes_king(piece, x, y, nx, ny, is_player)

    def move_piece(self, piece, nx, ny, is_player=True):
        team = self.player_pieces if is_player else self.ai_pieces
        opponent = self.ai_pieces if is_player else self.player_pieces
        if piece not in team:
            return False
        x, y = team[piece]

        if not self.valid_move(piece, x, y, nx, ny, is_player):
            return False

        for op, pos in list(opponent.items()):
            if pos == (nx, ny):
                del opponent[op]
                break

        self.board[x][y] = EMPTY
        self.board[nx][ny] = PIECES['player' if is_player else 'ai'][piece]
        team[piece] = (nx, ny)
        self.log_move(piece, nx, ny, is_player)
        return True

    def bot_move(self, is_player):
        team = self.player_pieces if is_player else self.ai_pieces
        for piece in ['knight', 'king']:
            if piece not in team:
                continue
            x, y = team[piece]
            candidates = [(x + dx, y + dy) for dx in [-2, -1, 0, 1, 2]
                          for dy in [-2, -1, 0, 1, 2] if (dx, dy) != (0, 0)]
            random.shuffle(candidates)
            for nx, ny in candidates:
                if self.move_piece(piece, nx, ny, is_player):
                    role = 'PlayerBot' if is_player else 'AIBot'
                    print(f"{role} plays: {piece.title()} to {self.indices_to_algebraic(nx, ny)}")
                    return

    def has_legal_moves(self, is_player):
        team = self.player_pieces if is_player else self.ai_pieces
        for piece, (x, y) in team.items():
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if self.valid_move(piece, x, y, nx, ny, is_player):
                        return True
        return False

    def checkmate(self, is_player):
        return self.in_check(is_player) and not self.has_legal_moves(is_player)

    def stalemate(self, is_player):
        return not self.in_check(is_player) and not self.has_legal_moves(is_player)

    def game_over(self):
        if 'king' not in self.player_pieces:
            print("🟥 AI wins! Player's king was captured.")
            return True
        if 'king' not in self.ai_pieces:
            print("🟩 Player wins! AI's king was captured.")
            return True
        if self.checkmate(True):
            print("🟥 AI wins by checkmate!")
            return True
        if self.checkmate(False):
            print("🟩 Player wins by checkmate!")
            return True
        if 'knight' not in self.player_pieces and 'knight' not in self.ai_pieces:
            print("🟨 Draw! Both knights are gone — insufficient material.")
            return True
        if self.stalemate(True):
            print("🟨 Draw! Player is stalemated.")
            return True
        if self.stalemate(False):
            print("🟨 Draw! AI is stalemated.")
            return True
        return False

    def print_log(self):
        print("\n📜 Move Log:")
        for i in range(0, len(self.move_log), 2):
            p = self.move_log[i]
            a = self.move_log[i+1] if i+1 < len(self.move_log) else ''
            print(f"{i//2 + 1}. {p:<6} {a}")
        print()

    def play(self):
        max_turns = 200
        turn_count = 0

        while turn_count < max_turns:
            self.display_board()
            is_player = (self.turn == 'player')
            self.bot_move(is_player)
            self.turn = 'ai' if is_player else 'player'
            turn_count += 1

            if self.game_over():
                self.display_board()
                self.print_log()
                return

        print("⏱️ Draw by turn limit!")
        self.display_board()
        self.print_log()

# Start the game
if __name__ == "__main__":
    game = MiniChess()
    game.play()