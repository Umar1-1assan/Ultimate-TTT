import tkinter as tk
import copy
import random

PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = ''

class SmallBoard:
    def __init__(self):
        # Initialize a 3x3 board with EMPTY cells
        self.board = [[EMPTY for _ in range(3)] for _ in range(3)]
        self.winner = None

    def place(self, r, c, player):
        # Place the player's mark if the cell is EMPTY
        if self.board[r][c] == EMPTY:
            self.board[r][c] = player
            self.winner = self.check_winner()
            return True
        return False

    def check_winner(self):
        b = self.board

        # Collect rows
        lines = []
        i = 0
        while i < 3:
            lines.append(b[i])
            i += 1

        # Collect columns using zip-like approach
        i = 0
        while i < 3:
            col = []
            j = 0
            while j < 3:
                col.append(b[j][i])
                j += 1
            lines.append(col)
            i += 1

        # Collect diagonals
        diag1 = []
        diag2 = []
        i = 0
        while i < 3:
            diag1.append(b[i][i])
            diag2.append(b[i][2 - i])
            i += 1
        lines.append(diag1)
        lines.append(diag2)

        # Check if any line has same non-empty values (a win)
        i = 0
        while i < len(lines):
            line = lines[i]
            if line[0] != EMPTY:
                all_equal = True
                j = 1
                while j < 3:
                    if line[j] != line[0]:
                        all_equal = False
                        break
                    j += 1
                if all_equal:
                    return line[0]
            i += 1

        # Check for a draw (no EMPTY cells)
        i = 0
        while i < 3:
            j = 0
            while j < 3:
                if b[i][j] == EMPTY:
                    return None
                j += 1
            i += 1
        return 'Draw'

    def is_full(self):
        # Check if board is completely filled
        i = 0
        while i < 3:
            j = 0
            while j < 3:
                if self.board[i][j] == EMPTY:
                    return False
                j += 1
            i += 1
        return True

    def get_available(self):
        # Get list of available (empty) positions on the board
        result = []
        r = 0
        while r < 3:
            c = 0
            while c < 3:
                if self.board[r][c] == EMPTY:
                    result.append((r, c))
                c += 1
            r += 1
        return result


class UltimateTicTacToe:
    def __init__(self):
        # Create 3x3 grid of SmallBoard instances
        self.boards = [[SmallBoard() for _ in range(3)] for _ in range(3)]
        self.macro_board = [[None for _ in range(3)] for _ in range(3)]  # Track winners of each small board
        self.active_board = None  # Which small board must be played on next (None = any)
        self.current_player = PLAYER_X  # X always starts

    def switch_player(self):
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

    def place_move(self, br, bc, sr, sc):
        board = self.boards[br][bc]
        if board.winner is not None:
            print(f"[Invalid] Small board ({br}, {bc}) already completed.")
            return False

        if self.active_board is not None and (br, bc) != self.active_board:
            print(f"[Invalid] Must play in the active board: {self.active_board}")
            return False

        if board.place(sr, sc, self.current_player):
            print(f"[Move] Player {self.current_player} played at Board({br},{bc}) Cell({sr},{sc})")
            if board.winner:
                print(f"[Result] Small Board ({br},{bc}) won by {board.winner}")
                self.macro_board[br][bc] = board.winner

            # Set next active board
            if self.boards[sr][sc].winner is None:
                self.active_board = (sr, sc)
                print(f"[Next] Active board set to ({sr},{sc})")
            else:
                self.active_board = None
                print("[Next] Active board is open (any available board)")

            self.switch_player()
            print(f"[Turn] Now it's {self.current_player}'s turn\n")
            return True
        else:
            print("[Invalid] That cell is already occupied.")
        return False

    def get_game_winner(self):
        b = self.macro_board

        # Build lines for rows
        lines = []
        i = 0
        while i < 3:
            lines.append(b[i])
            i += 1

        # Build lines for columns
        i = 0
        while i < 3:
            col = []
            j = 0
            while j < 3:
                col.append(b[j][i])
                j += 1
            lines.append(col)
            i += 1

        # Build lines for diagonals
        diag1 = []
        diag2 = []
        i = 0
        while i < 3:
            diag1.append(b[i][i])
            diag2.append(b[i][2 - i])
            i += 1
        lines.append(diag1)
        lines.append(diag2)

        # Check for win
        i = 0
        while i < len(lines):
            line = lines[i]
            if line[0] is not None:
                all_same = True
                j = 1
                while j < 3:
                    if line[j] != line[0]:
                        all_same = False
                        break
                    j += 1
                if all_same:
                    return line[0]
            i += 1

        # Check for draw
        i = 0
        while i < 3:
            j = 0
            while j < 3:
                if b[i][j] is None:
                    return None
                j += 1
            i += 1
        return 'Draw'

    def get_valid_moves(self):
        moves = []

        # If there’s an active board, restrict to that
        if self.active_board is not None:
            br, bc = self.active_board
            if self.boards[br][bc].winner is None:
                available = self.boards[br][bc].get_available()
                i = 0
                while i < len(available):
                    r, c = available[i]
                    moves.append((br, bc, r, c))
                    i += 1
                return moves

        # Otherwise, scan all boards for valid moves
        br = 0
        while br < 3:
            bc = 0
            while bc < 3:
                if self.boards[br][bc].winner is None:
                    available = self.boards[br][bc].get_available()
                    i = 0
                    while i < len(available):
                        r, c = available[i]
                        moves.append((br, bc, r, c))
                        i += 1
                bc += 1
            br += 1
        return moves


# ================= AI AGENTS =================

def mrv_heuristic(game):
    # Use Minimum Remaining Values (MRV) heuristic: pick move from board with fewest empty cells
    moves = game.get_valid_moves()
    i = 1
    min_move = moves[0]
    min_len = len(game.boards[min_move[0]][min_move[1]].get_available())
    while i < len(moves):
        move = moves[i]
        avail_len = len(game.boards[move[0]][move[1]].get_available())
        if avail_len < min_len:
            min_len = avail_len
            min_move = move
        i += 1
    return min_move

def forward_check(game, move):
    # Clone game, apply move, and check if at least one move remains
    br, bc, sr, sc = move
    temp_game = copy.deepcopy(game)
    temp_game.place_move(br, bc, sr, sc)
    return len(temp_game.get_valid_moves()) > 0

def ac3_check(game):
    # Simplified AC-3 check: ensure game isn’t already won
    return game.get_game_winner() is None

def csp_solver(game):
    moves = game.get_valid_moves()
    i = 0
    while i < len(moves):
        move = moves[i]
        if forward_check(game, move):
            return move
        i += 1
    return random.choice(moves) if moves else None


# ============ BASIC MINIMAX AGENT ============

def minimax(game, depth, maximizing):
    winner = game.get_game_winner()
    if winner == PLAYER_X:
        return 10
    elif winner == PLAYER_O:
        return -10
    elif winner == 'Draw' or depth == 0:
        return 0

    moves = game.get_valid_moves()
    if maximizing:
        max_eval = float('-inf')
        i = 0
        while i < len(moves):
            temp = copy.deepcopy(game)
            temp.place_move(*moves[i])
            eval = minimax(temp, depth - 1, False)
            if eval > max_eval:
                max_eval = eval
            i += 1
        return max_eval
    else:
        min_eval = float('inf')
        i = 0
        while i < len(moves):
            temp = copy.deepcopy(game)
            temp.place_move(*moves[i])
            eval = minimax(temp, depth - 1, True)
            if eval < min_eval:
                min_eval = eval
            i += 1
        return min_eval

def get_best_move_minimax(game, depth=3):
    best_val = float('-inf')
    best_move = None
    moves = game.get_valid_moves()
    i = 0
    while i < len(moves):
        temp = copy.deepcopy(game)
        temp.place_move(*moves[i])
        move_val = minimax(temp, depth - 1, False)
        if move_val > best_val:
            best_val = move_val
            best_move = moves[i]
        i += 1
    return best_move

### ========== GUI using tkinter ==========

import tkinter as tk

class GameGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultimate Tic Tac Toe")

        self.ai_vs_ai = True  # Toggle between human vs AI or AI vs AI

        self.game = UltimateTicTacToe()
        self.buttons = self.initialize_button_grid()

        self.create_gui()

        if self.ai_vs_ai:
            # Start the AI vs AI loop after 1 second
            self.master.after(1000, self.ai_vs_ai_move)

    def initialize_button_grid(self):
        """
        Initializes a 4-level nested list for buttons:
        [big_row][big_col][small_row][small_col]
        """
        return [[[[None for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]

    def create_gui(self):
        """
        Create a 3x3 grid of small boards. Each board contains 3x3 buttons.
        """
        for br in range(3):
            for bc in range(3):
                frame = tk.Frame(self.master, bg="black", bd=2)
                frame.grid(row=br, column=bc, padx=2, pady=2)
                for sr in range(3):
                    for sc in range(3):
                        btn = tk.Button(
                            frame, text="", font=('Helvetica', 16),
                            width=4, height=2,
                            command=lambda br=br, bc=bc, sr=sr, sc=sc: self.handle_click(br, bc, sr, sc)
                        )
                        btn.grid(row=sr, column=sc, padx=1, pady=1)
                        self.buttons[br][bc][sr][sc] = btn

    def handle_click(self, br, bc, sr, sc):
        """
        Handles human player moves. Does nothing if AI vs AI mode is enabled.
        """
        if self.ai_vs_ai:
            return

        print(f"[Player Click] Attempting move at Board({br},{bc}) Cell({sr},{sc})")
        if self.game.place_move(br, bc, sr, sc):
            self.update_gui()

            winner = self.game.get_game_winner()
            if winner:
                self.show_winner(winner)
                return

            # Trigger AI move after short delay
            self.master.after(500, self.ai_move)

    def ai_move(self):
        """
        Executes an AI move using the CSP solver.
        """
        print("[AI Thinking] Searching for best move...")
        move = csp_solver(self.game)
        if move:
            print(f"[AI Move] Playing at: {move}")
            self.game.place_move(*move)
            self.update_gui()

            winner = self.game.get_game_winner()
            if winner:
                self.show_winner(winner)
    itr = 0
    def ai_vs_ai_move(self):
        """
        Continuously make moves for both AI players.
        Alternates between CSP and Minimax-based AI.
        """
        print(f"[AI {self.game.current_player} Thinking]")

        if self.game.current_player == PLAYER_X:
            move = csp_solver(self.game)
        else:
            move = get_best_move_minimax(self.game, depth=2)
        self.itr+=1
        print(self.itr)

        if move:
            print(f"[AI {self.game.current_player} Move] {move}")
            self.game.place_move(*move)
            self.update_gui()

    def update_gui(self):
        """
        Updates button texts and states based on game state.
        Disables boards that are already won or inactive.
        """
        active = self.game.active_board

        for br in range(3):
            for bc in range(3):
                board = self.game.boards[br][bc]
                for sr in range(3):
                    for sc in range(3):
                        btn = self.buttons[br][bc][sr][sc]
                        btn.config(text=board.board[sr][sc])

                        # Disable buttons in won boards
                        if board.winner is not None:
                            btn.config(state='disabled', disabledforeground='red')
                        else:
                            # Enable only the buttons of the active board
                            if active is not None and (br, bc) != active:
                                btn.config(state='disabled')
                            else:
                                btn.config(state='normal')

        # Display which board is currently active
        if active:
            print(f"[GUI] Active board is: {active}")
        else:
            print("[GUI] Active board is open (any board allowed).")

        winner = self.game.get_game_winner()
        if self.ai_vs_ai and winner is None:
            # Continue AI vs AI play
            self.master.after(500, self.ai_vs_ai_move)
        elif winner:
            self.show_winner(winner)

    def show_winner(self, winner):
        """
        Displays the game result in a popup window and exits on confirmation.
        """
        print(f"[Game Over] Winner: {winner}")
        self.game_over = True

        popup = tk.Toplevel(self.master)
        popup.title("Game Over")
        popup.geometry("200x100")
        popup.resizable(False, False)

        message = f"{winner} wins!" if winner != "Draw" else "It's a draw!"
        tk.Label(popup, text=message, font=('Helvetica', 14)).pack(pady=10)

        def quit_all():
            popup.destroy()
            self.master.destroy()

        tk.Button(popup, text="Quit", font=('Helvetica', 12), command=quit_all).pack(pady=5)
        popup.protocol("WM_DELETE_WINDOW", quit_all)

# Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    game_gui = GameGUI(root)
    root.mainloop()
