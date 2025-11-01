import tkinter as tk
from tkinter import ttk, messagebox
import copy

class MinimaxTicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Minimax Tic-tac-toe Simulation")
        self.window.geometry("1200x800")
        self.window.configure(bg='#f0f0f0')
        
        # Trạng thái bàn cờ ban đầu (đã có vài nước đi)
        # X = 1, O = -1, Empty = 0
        self.board = [
            [1, 0, -1],   # X ở (0,0), O ở (0,2)
            [0, 1, 0],    # X ở (1,1)
            [0, 0, 0]     # Hàng dưới trống
        ]
        
        self.current_player = -1  # Lượt O (MIN)
        self.game_tree = []
        self.step_index = 0
        
        self.setup_ui()
        self.update_board_display()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Game board
        left_panel = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Title
        title_label = tk.Label(left_panel, text="Tic-tac-toe Minimax", 
                              font=('Arial', 16, 'bold'), bg='#ffffff')
        title_label.pack(pady=10)
        
        # Game board
        self.board_frame = tk.Frame(left_panel, bg='#ffffff')
        self.board_frame.pack(pady=10)
        
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(self.board_frame, text='', width=6, height=3,
                               font=('Arial', 20, 'bold'),
                               command=lambda r=i, c=j: self.make_move(r, c))
                btn.grid(row=i, column=j, padx=2, pady=2)
                row.append(btn)
            self.buttons.append(row)
        
        # Control buttons
        control_frame = tk.Frame(left_panel, bg='#ffffff')
        control_frame.pack(pady=20)
        
        self.run_btn = tk.Button(control_frame, text="Chạy Minimax", 
                                font=('Arial', 12, 'bold'),
                                bg='#4CAF50', fg='white',
                                command=self.run_minimax)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_btn = tk.Button(control_frame, text="Bước tiếp theo", 
                                 font=('Arial', 12, 'bold'),
                                 bg='#2196F3', fg='white',
                                 command=self.next_step)
        self.step_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(control_frame, text="Reset", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#f44336', fg='white',
                                  command=self.reset_game)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Minimax tree
        right_panel = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Tree title
        tree_title = tk.Label(right_panel, text="Cây Quyết định Minimax", 
                             font=('Arial', 14, 'bold'), bg='#ffffff')
        tree_title.pack(pady=10)
        
        # Legend
        legend_frame = tk.Frame(right_panel, bg='#ffffff')
        legend_frame.pack(pady=5)
        
        tk.Label(legend_frame, text="MAX (X): ", font=('Arial', 10, 'bold'), 
                bg='#ffffff', fg='#d32f2f').pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Cố gắng thắng  ", font=('Arial', 10), 
                bg='#ffffff').pack(side=tk.LEFT)
        tk.Label(legend_frame, text="MIN (O): ", font=('Arial', 10, 'bold'), 
                bg='#ffffff', fg='#1976d2').pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Cố gắng chặn", font=('Arial', 10), 
                bg='#ffffff').pack(side=tk.LEFT)
        
        # Tree display
        self.tree_frame = tk.Frame(right_panel, bg='#ffffff')
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(right_panel, text="Sẵn sàng chạy Minimax", 
                                    font=('Arial', 12), bg='#ffffff')
        self.status_label.pack(pady=10)
        
    def update_board_display(self):
        for i in range(3):
            for j in range(3):
                btn = self.buttons[i][j]
                if self.board[i][j] == 1:
                    btn.config(text='X', bg='#ffcdd2', fg='#d32f2f')
                elif self.board[i][j] == -1:
                    btn.config(text='O', bg='#e3f2fd', fg='#1976d2')
                else:
                    btn.config(text='', bg='#f5f5f5', fg='black')
    
    def make_move(self, row, col):
        if self.board[row][col] == 0:
            self.board[row][col] = self.current_player
            self.current_player *= -1
            self.update_board_display()
            self.clear_tree_display()
    
    def evaluate_board(self, board):
        # Kiểm tra thắng thua
        # Hàng
        for row in board:
            if abs(sum(row)) == 3:
                return sum(row) // 3
        
        # Cột
        for col in range(3):
            col_sum = sum(board[row][col] for row in range(3))
            if abs(col_sum) == 3:
                return col_sum // 3
        
        # Đường chéo
        diag1 = board[0][0] + board[1][1] + board[2][2]
        diag2 = board[0][2] + board[1][1] + board[2][0]
        
        if abs(diag1) == 3:
            return diag1 // 3
        if abs(diag2) == 3:
            return diag2 // 3
        
        return 0  # Hòa hoặc chưa kết thúc
    
    def is_terminal(self, board):
        # Kiểm tra thắng thua
        if self.evaluate_board(board) != 0:
            return True
        
        # Kiểm tra bàn cờ đầy
        for row in board:
            if 0 in row:
                return False
        return True
    
    def get_possible_moves(self, board):
        moves = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    moves.append((i, j))
        return moves
    
    def minimax(self, board, depth, is_maximizing, alpha=float('-inf'), beta=float('inf')):
        score = self.evaluate_board(board)
        
        # Điều kiện dừng
        if score != 0:
            return score
        
        if self.is_terminal(board) or depth == 0:
            return score
        
        moves = self.get_possible_moves(board)
        
        if is_maximizing:  # MAX player (X)
            max_eval = float('-inf')
            for move in moves:
                new_board = copy.deepcopy(board)
                new_board[move[0]][move[1]] = 1
                eval_score = self.minimax(new_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:  # MIN player (O)
            min_eval = float('inf')
            for move in moves:
                new_board = copy.deepcopy(board)
                new_board[move[0]][move[1]] = -1
                eval_score = self.minimax(new_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_best_move(self, board, is_maximizing):
        best_move = None
        moves_with_scores = []
        
        if is_maximizing:
            best_score = float('-inf')
            player = 1
        else:
            best_score = float('inf')
            player = -1
        
        moves = self.get_possible_moves(board)
        
        for move in moves:
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = player
            score = self.minimax(new_board, 4, not is_maximizing)
            moves_with_scores.append((move, score))
            
            if is_maximizing and score > best_score:
                best_score = score
                best_move = move
            elif not is_maximizing and score < best_score:
                best_score = score
                best_move = move
        
        return best_move, best_score, moves_with_scores
    
    def run_minimax(self):
        if self.is_terminal(self.board):
            messagebox.showinfo("Game Over", "Trò chơi đã kết thúc!")
            return
        
        is_maximizing = self.current_player == 1
        player_name = "MAX (X)" if is_maximizing else "MIN (O)"
        
        best_move, best_score, all_moves = self.get_best_move(self.board, is_maximizing)
        
        self.display_minimax_tree(all_moves, best_move, is_maximizing)
        
        self.status_label.config(
            text=f"{player_name} chọn nước đi tối ưu: ({best_move[0]}, {best_move[1]}) với điểm {best_score}"
        )
        
        # Thực hiện nước đi tối ưu
        if best_move:
            self.board[best_move[0]][best_move[1]] = self.current_player
            self.current_player *= -1
            self.update_board_display()
    
    def display_minimax_tree(self, moves_with_scores, best_move, is_maximizing):
        self.clear_tree_display()
        
        player_color = '#d32f2f' if is_maximizing else '#1976d2'
        player_name = "MAX (X)" if is_maximizing else "MIN (O)"
        
        # Header
        header = tk.Label(self.tree_frame, 
                         text=f"Phân tích nước đi cho {player_name}",
                         font=('Arial', 12, 'bold'),
                         bg='#ffffff', fg=player_color)
        header.pack(pady=5)
        
        # Moves analysis
        for i, (move, score) in enumerate(moves_with_scores):
            move_frame = tk.Frame(self.tree_frame, bg='#ffffff', relief=tk.RIDGE, bd=1)
            move_frame.pack(fill=tk.X, pady=2, padx=10)
            
            is_best = (move == best_move)
            bg_color = '#e8f5e8' if is_best else '#f9f9f9'
            move_frame.config(bg=bg_color)
            
            move_text = f"Nước đi ({move[0]}, {move[1]}): Điểm = {score}"
            if is_best:
                move_text += " ⭐ (TỐI ƯU)"
            
            label = tk.Label(move_frame, text=move_text,
                           font=('Arial', 10, 'bold' if is_best else 'normal'),
                           bg=bg_color, fg=player_color)
            label.pack(pady=5)
            
            # Hiển thị logic
            if is_maximizing:
                logic = "MAX cố gắng tối đa hóa điểm số để thắng"
            else:
                logic = "MIN cố gắng tối thiểu hóa điểm số để chặn MAX"
            
            logic_label = tk.Label(move_frame, text=logic,
                                 font=('Arial', 8), bg=bg_color, fg='gray')
            logic_label.pack()
    
    def clear_tree_display(self):
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
    
    def next_step(self):
        # Placeholder cho chức năng bước tiếp theo
        self.run_minimax()
    
    def reset_game(self):
        # Reset về trạng thái ban đầu
        self.board = [
            [1, 0, -1],
            [0, 1, 0],
            [0, 0, 0]
        ]
        self.current_player = -1
        self.update_board_display()
        self.clear_tree_display()
        self.status_label.config(text="Sẵn sàng chạy Minimax")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = MinimaxTicTacToe()
    game.run()

du lich
dui qua
