import pygame
import sys
from collections import defaultdict

class Piece:
    SIZE_ORDER = {'S': 1, 'M': 2, 'L': 3}
    RADIUS = {'S': 15, 'M': 25, 'L': 35}

    def __init__(self, size, player):
        self.size = size
        self.player = player

    def __repr__(self):
        return f"{self.size}{self.player}"


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
        return self.stack[-1] if self.stack else None


class Game:
    def __init__(self):
        self.board = [[Cell() for _ in range(3)] for _ in range(3)]
        self.pieces_remaining = {
            1: {'S': 3, 'M': 3, 'L': 3},
            2: {'S': 3, 'M': 3, 'L': 3}
        }
        self.current_player = 1
        self.selected_size = 'S'
        self.game_over = False
        self.winner = None

    def take_turn(self, x, y):
        if self.game_over:
            return False

        if not (0 <= x < 3 and 0 <= y < 3):
            return False

        size = self.selected_size
        if self.pieces_remaining[self.current_player][size] <= 0:
            return False

        piece = Piece(size, self.current_player)
        cell = self.board[y][x]

        if not cell.place_piece(piece):
            return False

        self.pieces_remaining[self.current_player][size] -= 1

        if self.check_win():
            self.game_over = True
            self.winner = self.current_player
        else:
            self.current_player = 2 if self.current_player == 1 else 1
        return True

    def check_win(self):
        lines = []

        for i in range(3):
            lines.append([self.board[i][j] for j in range(3)])
            lines.append([self.board[j][i] for j in range(3)])

        lines.append([self.board[i][i] for i in range(3)])
        lines.append([self.board[i][2 - i] for i in range(3)])

        for line in lines:
            if self.check_same_size_line(line) or self.check_sequence_line(line):
                return True

        for row in self.board:
            for cell in row:
                if self.check_concentric(cell):
                    return True
        return False

    def check_same_size_line(self, line):
        sizes, owners = [], []
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
            if not top:
                return False
            sizes.append(Piece.SIZE_ORDER[top.size])
            owners.append(top.player)

        if not all(owner == owners[0] for owner in owners):
            return False

        if len(set(sizes)) != 3:
            return False

        return sizes == sorted(sizes) or sizes == sorted(sizes, reverse=True)


    def check_concentric(self, cell):
        if len(cell.stack) != 3:
            return False
        sizes = {p.size for p in cell.stack}
        owners = {p.player for p in cell.stack}
        return sizes == {'S', 'M', 'L'} and len(owners) == 1
    
    def reset_game(self):
        self.__init__()

CELL_SIZE = 200
SCREEN_SIZE = 600
BG_COLOR = (240, 240, 240)
GRID_COLOR = (0, 0, 0)
COLORS = {1: (200, 0, 0), 2: (0, 0, 200)}

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 140))
pygame.display.set_caption("Digital Otrio")
font = pygame.font.SysFont(None, 30)
game = Game()


def draw_board():
    screen.fill(BG_COLOR)

    for i in range(1, 3):
        pygame.draw.line(screen, GRID_COLOR, (0, i * CELL_SIZE), (SCREEN_SIZE, i * CELL_SIZE), 3)
        pygame.draw.line(screen, GRID_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, SCREEN_SIZE), 3)

    for y in range(3):
        for x in range(3):
            cell = game.board[y][x]
            center_x = x * CELL_SIZE + CELL_SIZE // 2
            center_y = y * CELL_SIZE + CELL_SIZE // 2
            for piece in sorted(cell.stack, key=lambda p: Piece.SIZE_ORDER[p.size]):
                pygame.draw.circle(
                    screen,
                    COLORS[piece.player],
                    (center_x, center_y),
                    Piece.RADIUS[piece.size],
                    3
                )

    pygame.draw.rect(screen, (220, 220, 220), (0, SCREEN_SIZE, SCREEN_SIZE, 140))

    info_text = f"Player {game.current_player} | Selected Size: {game.selected_size} | Remaining: {game.pieces_remaining[game.current_player]}"
    text_surface = font.render(info_text, True, (0, 0, 0))
    screen.blit(text_surface, (10, SCREEN_SIZE + 10))

    subtitle_text = 'Press "S", "M", or "L" to change piece size.'
    subtitle_surface = font.render(subtitle_text, True, (100, 100, 100))
    screen.blit(subtitle_surface, (10, SCREEN_SIZE + 40))

    if game.game_over:
        win_text = f"Player {game.winner} wins! Press 'R' to restart."
        win_surface = font.render(win_text, True, (0, 128, 0))
        screen.blit(win_surface, (10, SCREEN_SIZE + 80))

    pygame.display.flip()


def handle_click(pos):
    x, y = pos
    if y > SCREEN_SIZE:
        return

    cell_x = x // CELL_SIZE
    cell_y = y // CELL_SIZE
    game.take_turn(cell_x, cell_y)


def handle_key(key):
    if key == pygame.K_s:
        game.selected_size = 'S'
    elif key == pygame.K_m:
        game.selected_size = 'M'
    elif key == pygame.K_l:
        game.selected_size = 'L'
    elif key == pygame.K_r and game.game_over:
        game.reset_game()

clock = pygame.time.Clock()
running = True

while running:
    draw_board()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            handle_key(event.key)

    clock.tick(60)

pygame.quit()
sys.exit()
