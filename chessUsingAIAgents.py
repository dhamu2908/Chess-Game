import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Chessboard setup
class Piece:
    def __init__(self, name, color, row, col, first_move=False):
        self.name = name
        self.color = color
        self.row = row
        self.col = col
        self.first_move = first_move  # Track if the piece has moved
        self.has_moved = False  # For castling and en passant

    def draw(self, win):
        font = pygame.font.Font(None, 36)
        if self.name == 'knight':
            text = font.render('N', True, BLUE if self.color == 'white' else BLACK)
        elif self.name == 'king':
            text = font.render('K', True, RED if self.color == 'white' else BLACK)
        else:
            text = font.render(self.name[0].upper(), True, BLUE if self.color == 'white' else BLACK)
        text_rect = text.get_rect(center=(self.col * SQUARE_SIZE + SQUARE_SIZE // 2, self.row * SQUARE_SIZE + SQUARE_SIZE // 2))
        win.blit(text, text_rect)

    def get_possible_moves(self, board):
        moves = []
        if self.name == 'pawn':
            direction = -1 if self.color == 'white' else 1
            new_row = self.row + direction

            # Normal move (1 square)
            if 0 <= new_row < 8 and board[new_row][self.col] is None:
                moves.append((new_row, self.col))

            # First move (2 squares)
            if self.first_move:
                new_row_2 = self.row + 2 * direction
                if 0 <= new_row_2 < 8 and board[new_row_2][self.col] is None:
                    moves.append((new_row_2, self.col))

            # Capture diagonally
            for d_col in [-1, 1]:
                new_col = self.col + d_col
                if 0 <= new_col < 8 and 0 <= new_row < 8:
                    if board[new_row][new_col] and board[new_row][new_col].color != self.color:
                        moves.append((new_row, new_col))

            # En passant
            if self.row == 3 or self.row == 4:  # Only for pawns in the en passant row
                for d_col in [-1, 1]:
                    new_col = self.col + d_col
                    if 0 <= new_col < 8:
                        adjacent_piece = board[self.row][new_col]
                        if adjacent_piece and adjacent_piece.name == 'pawn' and adjacent_piece.color != self.color:
                            moves.append((new_row, new_col))

        elif self.name == 'rook':
            # Horizontal and vertical moves
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
            for dr, dc in directions:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None:
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break  # Stop if an opponent's piece is encountered
                    else:
                        break  # Stop if own piece is encountered
                    r += dr
                    c += dc

        elif self.name == 'knight':
            # L-shaped moves
            knight_moves = [
                (-2, -1), (-2, 1), (2, -1), (2, 1),
                (-1, -2), (-1, 2), (1, -2), (1, 2)
            ]
            for move in knight_moves:
                new_row, new_col = self.row + move[0], self.col + move[1]
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if board[new_row][new_col] is None or board[new_row][new_col].color != self.color:
                        moves.append((new_row, new_col))

        elif self.name == 'bishop':
            # Diagonal moves
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Four diagonal directions
            for dr, dc in directions:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None:
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break  # Stop if an opponent's piece is encountered
                    else:
                        break  # Stop if own piece is encountered
                    r += dr
                    c += dc

        elif self.name == 'queen':
            # Rook and bishop moves combined
            moves.extend(Piece('rook', self.color, self.row, self.col).get_possible_moves(board))
            moves.extend(Piece('bishop', self.color, self.row, self.col).get_possible_moves(board))

        elif self.name == 'king':
            # King moves one square in any direction
            king_moves = [
                (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)
            ]
            for move in king_moves:
                new_row, new_col = self.row + move[0], self.col + move[1]
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if board[new_row][new_col] is None or board[new_row][new_col].color != self.color:
                        moves.append((new_row, new_col))

            # Castling
            if not self.has_moved:
                # Kingside castling
                if board[self.row][7] and board[self.row][7].name == 'rook' and not board[self.row][7].has_moved:
                    if board[self.row][5] is None and board[self.row][6] is None:
                        moves.append((self.row, 6))

                # Queenside castling
                if board[self.row][0] and board[self.row][0].name == 'rook' and not board[self.row][0].has_moved:
                    if board[self.row][1] is None and board[self.row][2] is None and board[self.row][3] is None:
                        moves.append((self.row, 2))

        return moves

# Initialize board with pieces
def initialize_board():
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]

    # Black pieces
    board[0][0] = Piece('rook', 'black', 0, 0)
    board[0][7] = Piece('rook', 'black', 0, 7)
    board[0][1] = Piece('knight', 'black', 0, 1)
    board[0][6] = Piece('knight', 'black', 0, 6)
    board[0][2] = Piece('bishop', 'black', 0, 2)
    board[0][5] = Piece('bishop', 'black', 0, 5)
    board[0][3] = Piece('queen', 'black', 0, 3)
    board[0][4] = Piece('king', 'black', 0, 4)
    for i in range(COLS):
        board[1][i] = Piece('pawn', 'black', 1, i, first_move=True)

    # White pieces
    board[7][0] = Piece('rook', 'white', 7, 0)
    board[7][7] = Piece('rook', 'white', 7, 7)
    board[7][1] = Piece('knight', 'white', 7, 1)
    board[7][6] = Piece('knight', 'white', 7, 6)
    board[7][2] = Piece('bishop', 'white', 7, 2)
    board[7][5] = Piece('bishop', 'white', 7, 5)
    board[7][3] = Piece('queen', 'white', 7, 3)
    board[7][4] = Piece('king', 'white', 7, 4)
    for i in range(COLS):
        board[6][i] = Piece('pawn', 'white', 6, i, first_move=True)

    return board

def draw_board(win):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(win):
    for row in board:
        for piece in row:
            if piece:
                piece.draw(win)

def get_square_from_mouse(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def is_in_check(board, color):
    # Find the king's position
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.name == 'king' and piece.color == color:
                king_pos = (row, col)
                break
        if king_pos:
            break

    if not king_pos:
        return False  # No king found (should not happen in a valid game)

    # Check if any opponent's piece can attack the king
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.color != color:
                if king_pos in piece.get_possible_moves(board):
                    return True
    return False

def simulate_move(board, piece, move):
    # Simulate a move and return the new board state
    temp_board = [row[:] for row in board]
    temp_board[piece.row][piece.col] = None
    temp_board[move[0]][move[1]] = piece
    return temp_board

def get_valid_moves(piece, board):
    # Get all possible moves and filter out moves that leave the king in check
    possible_moves = piece.get_possible_moves(board)
    valid_moves = []
    for move in possible_moves:
        temp_board = simulate_move(board, piece, move)
        if not is_in_check(temp_board, piece.color):
            valid_moves.append(move)
    return valid_moves

def is_in_check(board, color):
    # Find the king's position
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.name == 'king' and piece.color == color:
                king_pos = (row, col)
                break
        if king_pos:
            break

    if not king_pos:
        return False  # No king found (should not happen in a valid game)

    # Check if any opponent's piece can attack the king
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.color != color:
                if king_pos in piece.get_possible_moves(board):
                    return True
    return False

def is_checkmate(board, color):
    # Check if the king is in check and has no legal moves
    if not is_in_check(board, color):
        return False

    # Check if any move can get the king out of check
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.color == color:
                valid_moves = get_valid_moves(piece, board)
                if valid_moves:
                    return False  # There is at least one move to escape check
    return True  # No moves to escape check

def ai_move():
    global turn
    possible_moves = []
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece and piece.color == 'black':
                valid_moves = get_valid_moves(piece, board)
                if valid_moves:
                    possible_moves.append((piece, random.choice(valid_moves)))
    if possible_moves:
        piece, move = random.choice(possible_moves)
        board[piece.row][piece.col] = None
        piece.row, piece.col = move
        board[move[0]][move[1]] = piece
        turn = 'white'

    # Add delay to slow down the AI's move
    pygame.time.delay(1000)  # Delay for 1000 milliseconds (1 second)

def draw_possible_moves(win, selected_piece):
    if selected_piece:
        moves = selected_piece.get_possible_moves(board)
        for move in moves:
            # Draw dots for possible moves in green
            pygame.draw.circle(win, GREEN, (move[1] * SQUARE_SIZE + SQUARE_SIZE // 2, move[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 5)

def draw_game_over(win, winner):
    font = pygame.font.Font(None, 74)
    text = font.render(f'{winner} wins!', True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    win.blit(text, text_rect)

    font = pygame.font.Font(None, 36)
    text = font.render('Press R to restart', True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    win.blit(text, text_rect)

def main():
    global board, turn
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reactive Chess")
    clock = pygame.time.Clock()
    selected_piece = None
    turn = 'white'
    game_over = False
    winner = None
    
    board = initialize_board()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == 'white' and not game_over:
                row, col = get_square_from_mouse(pygame.mouse.get_pos())
                if selected_piece:
                    valid_moves = get_valid_moves(selected_piece, board)
                    if (row, col) in valid_moves:
                        # Move the selected piece to the clicked square
                        board[selected_piece.row][selected_piece.col] = None
                        board[row][col] = selected_piece
                        selected_piece.row, selected_piece.col = row, col
                        selected_piece.first_move = False  # Mark the piece as moved
                        turn = 'black'  # Switch turn to black
                    selected_piece = None  # Deselect the piece
                elif board[row][col] and board[row][col].color == turn:
                    selected_piece = board[row][col]  # Select the piece
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # Restart the game
                    board = initialize_board()
                    turn = 'white'
                    game_over = False
                    winner = None
        
        if not game_over:
            if turn == 'black':
                ai_move()
            
            # Check for checkmate
            if is_checkmate(board, 'white'):
                game_over = True
                winner = 'Black'
            elif is_checkmate(board, 'black'):
                game_over = True
                winner = 'White'

        draw_board(win)
        draw_pieces(win)
        if selected_piece:
            draw_possible_moves(win, selected_piece)  # Draw valid moves for the selected piece

        if game_over:
            draw_game_over(win, winner)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()