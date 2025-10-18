from collections import defaultdict

# Represents every piece on board
class Piece:
    SIZE_ORDER = {'S': 1, 'M': 2, 'L': 3}
    
    def __init__(self, size, player):
        self.size = size  # 'S', 'M', or 'L'
        self.player = player  # Player 1 or Player 2

    def __repr__(self):
        return f"{self.size}{self.player}"

# Represents every cell on the board (9 total)
class Cell:
    def __init__(self):
        self.stack = []

    def place_piece(self, piece):
        sizes_in_cell = {p.size for p in self.stack}
        if piece.size in sizes_in_cell:
            return False
        if len(self.stack) >= 3:
            return False
        self.stack.append(piece)
        return True

    def get_top_piece(self):
        if self.stack:
            return self.stack[-1]
        return None

    def __repr__(self):
        return "[" + " ".join(str(p) for p in self.stack) + "]"

# Main game logic
class Game:
    def __init__(self):
        self.board = [[Cell() for _ in range(3)] for _ in range(3)] # 3x3 grid
        self.pieces_remaining = {
            1: {'S': 3, 'M': 3, 'L': 3},
            2: {'S': 3, 'M': 3, 'L': 3}
        }
        self.current_player = 1
        self.game_over = False

    def display_board(self):
        print("\n      0          1          2")
        for row_idx, row in enumerate(self.board):
            row_str = f"{row_idx} "
            for cell in row:
                content = " ".join(str(p) for p in cell.stack) if cell.stack else "        "
                row_str += f"[{content:^8}] "
            print(row_str)

    def valid_coords(self, x, y):
        return 0 <= x < 3 and 0 <= y < 3

    def take_turn(self, size, x, y):
        if self.game_over:
            print("Game is over!")
            return

        size = size.upper()
        if size not in ('S', 'M', 'L'):
            print("Invalid size. Choose S, M, or L.")
            return

        if not self.valid_coords(x, y):
            print("Invalid coordinates.")
            return

        if self.pieces_remaining[self.current_player][size] <= 0:
            print("No pieces of that size left.")
            return

        piece = Piece(size, self.current_player)
        cell = self.board[y][x]
        if not cell.place_piece(piece):
            print("Cannot place piece there.")
            return

        self.pieces_remaining[self.current_player][size] -= 1
        self.display_board()

        if self.check_win():
            print(f"\n*** Player {self.current_player} wins! ***")
            self.game_over = True
            return

        self.current_player = 2 if self.current_player == 1 else 1

    def check_win(self):
        lines = []

        # Rows and columns
        for i in range(3):
            lines.append([self.board[i][j] for j in range(3)])  # row
            lines.append([self.board[j][i] for j in range(3)])  # column

        # Diagonals
        lines.append([self.board[i][i] for i in range(3)])
        lines.append([self.board[i][2 - i] for i in range(3)])

        for line in lines:
            if self.check_same_size_line(line):
                return True
            if self.check_sequence_line(line):
                return True

        # All three pieces in the same cell
        for row in self.board:
            for cell in row:
                if self.check_concentric(cell):
                    return True

        return False

    def check_same_size_line(self, line):
        sizes = []
        owners = []
        for cell in line:
            top = cell.get_top_piece()
            if top:
                sizes.append(top.size)
                owners.append(top.player)
            else:
                return False
        return all(s == sizes[0] for s in sizes) and all(p == owners[0] for p in owners)

    def check_sequence_line(self, line):
        sizes = []
        owners = []
        for cell in line:
            top = cell.get_top_piece()
            if top:
                sizes.append(Piece.SIZE_ORDER[top.size])
                owners.append(top.player)
            else:
                return False
        return (
            owners.count(owners[0]) == 3 and
            (sizes == [1, 2, 3] or sizes == [3, 2, 1])
        )

    def check_concentric(self, cell):
        if len(cell.stack) != 3:
            return False
        sizes = {p.size for p in cell.stack}
        owners = {p.player for p in cell.stack}
        return sizes == {'S', 'M', 'L'} and len(owners) == 1

    def play(self):
        print("*** Welcome to Digital Otrio! ***")
        self.display_board()
        while not self.game_over:
            print(f"\nPlayer {self.current_player}'s turn.")
            print(f"Remaining pieces: {self.pieces_remaining[self.current_player]}")
            try:
                size = input("Enter piece size (S/M/L): ").strip().upper()
                x = int(input("Enter column (0-2): "))
                y = int(input("Enter row (0-2): "))
                self.take_turn(size, x, y)
            except Exception as e:
                print("Invalid input, try again.")

if __name__ == "__main__":
    game = Game()
    game.play()
