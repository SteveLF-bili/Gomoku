import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import random
import math
from functools import lru_cache
import time

class Gomoku:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("五子棋")
        self.window.geometry("1200x800")
        self.window.configure(bg="#c5c5c5")
        self.window.resizable(False, False)
        
        # 游戏参数
        self.BOARD_SIZE = 15
        self.CELL_SIZE = 45
        self.MARGIN = 50
        self.PIECE_RADIUS = 18
        
        # 计算棋盘实际大小
        self.BOARD_PIXEL_SIZE = (self.BOARD_SIZE - 1) * self.CELL_SIZE + 2 * self.MARGIN
        
        # 游戏状态
        self.board = None
        self.current_player = 1
        self.game_mode = None
        self.difficulty = "medium"
        self.game_over = False
        self.winner = None
        self.last_move = None  # 记录最后落子位置
        
        # 初始化界面
        self.setup_ui()
        self.show_menu()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = tk.Frame(self.window, bg="#c5c5c5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左侧：棋盘区域
        left_frame = tk.Frame(main_frame, bg='#c5c5c5')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 棋盘画布
        canvas_container = tk.Frame(left_frame, bg='#8B4513', relief=tk.RAISED, bd=3)
        canvas_container.pack(pady=10)
        
        self.canvas = tk.Canvas(canvas_container, 
                               width=self.BOARD_PIXEL_SIZE, 
                               height=self.BOARD_PIXEL_SIZE,
                               bg='#DEB887', highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)
        
        # 右侧：控制面板
        right_frame = tk.Frame(main_frame, bg='#c5c5c5', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(30, 0))
        right_frame.pack_propagate(False)
        
        # 游戏标题
        title_label = tk.Label(right_frame, text="五子棋", 
                              font=('微软雅黑', 36, 'bold'),
                              bg='#c5c5c5', fg='#FFD700')
        title_label.pack(pady=(20, 30))
        
        # 模式选择区域
        mode_frame = tk.Frame(right_frame, bg='#c5c5c5')
        mode_frame.pack(fill=tk.X, pady=10)
        
        mode_label = tk.Label(mode_frame, text="游戏模式", 
                             font=('微软雅黑', 16, 'bold'),
                             bg='#c5c5c5', fg='#FFD700')
        mode_label.pack(anchor=tk.W)
        
        # 模式按钮
        self.pvp_btn = self.create_styled_button(right_frame, "👥 玩家对战", 
                                                  self.start_pvp, '#4CAF50')
        self.pvp_btn.pack(pady=5, fill=tk.X)
        
        self.pvc_btn = self.create_styled_button(right_frame, "🤖 人机对战", 
                                                  self.start_pvc, '#2196F3')
        self.pvc_btn.pack(pady=5, fill=tk.X)
        
        # 难度选择
        self.difficulty_frame = tk.Frame(right_frame, bg='#c5c5c5')
        self.difficulty_frame.pack(fill=tk.X, pady=20)
        self.difficulty_frame.pack_forget()
        
        difficulty_label = tk.Label(self.difficulty_frame, text="AI 难度", 
                                   font=('微软雅黑', 14, 'bold'),
                                   bg='#c5c5c5', fg='black')
        difficulty_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.difficulty_var = tk.StringVar(value="medium")
        difficulties = [
            ("🎯 简单", "easy"),
            ("⚡ 中等", "medium"),
            ("🔥 困难", "hard")
        ]
        
        for text, value in difficulties:
            rb = tk.Radiobutton(self.difficulty_frame, text=text, 
                               variable=self.difficulty_var, value=value,
                               bg='#c5c5c5', fg='black', 
                               selectcolor='#c5c5c5', activebackground='#c5c5c5',
                               font=('微软雅黑', 11))
            rb.pack(anchor=tk.W, pady=2)
        
        # 状态显示区域
        self.status_frame = tk.Frame(right_frame, bg='#8B5A2B', relief=tk.RAISED, bd=3)
        self.status_frame.pack(fill=tk.X, pady=30)
        
        # 状态标题
        status_title = tk.Label(self.status_frame, text="游戏状态", 
                               font=('微软雅黑', 14, 'bold'),
                               bg='#8B5A2B', fg='#FFD700')
        status_title.pack(pady=(10, 5))
        
        # 分隔线
        separator = tk.Frame(self.status_frame, height=2, bg='#D2691E')
        separator.pack(fill=tk.X, padx=20, pady=5)
        
        # 主要状态信息
        self.status_label = tk.Label(self.status_frame, text="⚫ 黑棋先手", 
                                     font=('微软雅黑', 16, 'bold'), 
                                     bg='#8B5A2B', fg='white',
                                     height=2)
        self.status_label.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        # 次要状态信息
        self.player_indicator = tk.Label(self.status_frame, text="请选择游戏模式", 
                                         font=('微软雅黑', 12), 
                                         bg='#8B5A2B', fg='#EEEEEE')
        self.player_indicator.pack(pady=(0, 15))
        
        # 胜利信息显示区域
        self.victory_frame = tk.Frame(self.status_frame, bg='#D2691E', relief=tk.SUNKEN, bd=2)
        self.victory_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        self.victory_frame.pack_forget()
        
        self.victory_label = tk.Label(self.victory_frame, text="", 
                                     font=('微软雅黑', 14, 'bold'),
                                     bg='#D2691E', fg='#FFD700',
                                     height=2)
        self.victory_label.pack(fill=tk.X, padx=10, pady=5)
        
        # 控制按钮
        self.restart_btn = self.create_styled_button(right_frame, "🔄 重新开始", 
                                                      self.restart_game, '#FF9800')
        self.restart_btn.pack(pady=5, fill=tk.X)
        self.restart_btn.config(state=tk.DISABLED)
        
        self.back_btn = self.create_styled_button(right_frame, "🏠 返回主菜单", 
                                                   self.show_menu, '#9C27B0')
        self.back_btn.pack(pady=5, fill=tk.X)
        
        # 游戏信息
        info_frame = tk.Frame(right_frame, bg='#c5c5c5')
        info_frame.pack(fill=tk.X, pady=30)
        
        info_text = """游戏规则：
• 黑棋先手，白棋后手
• 先形成五子连珠者胜
• 点击棋盘交叉点落子"""
        
        info_label = tk.Label(info_frame, text=info_text, 
                             font=('微软雅黑', 10), 
                             bg='#c5c5c5', fg='#CCCCCC',
                             justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
    def create_styled_button(self, parent, text, command, bg_color):
        """创建样式按钮"""
        btn = tk.Button(parent, text=text, font=('微软雅黑', 12, 'bold'),
                       bg=bg_color, fg='white', relief=tk.RAISED, bd=3,
                       command=command, cursor='hand2', padx=15, pady=8)
        
        def on_enter(e):
            btn.config(bg=self.lighten_color(bg_color))
            
        def on_leave(e):
            btn.config(bg=bg_color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def lighten_color(self, color):
        """使颜色变亮"""
        if color == '#4CAF50':
            return '#66BB6A'
        elif color == '#2196F3':
            return '#42A5F5'
        elif color == '#FF9800':
            return '#FFA726'
        elif color == '#9C27B0':
            return '#AB47BC'
        return color
        
    def show_victory_message(self, winner, is_draw=False):
        """显示胜利/平局信息"""
        self.victory_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        if is_draw:
            self.victory_label.config(text="🤝 平局！", fg='#FFD700')
            self.status_label.config(text="🤝 游戏结束 - 平局")
        else:
            if winner == 1:
                self.victory_label.config(text="🏆 黑棋胜利！ 🏆", fg='#FFD700')
                self.status_label.config(text="⚫ 恭喜黑棋获胜！")
            else:
                self.victory_label.config(text="🏆 白棋胜利！ 🏆", fg='#FFD700')
                self.status_label.config(text="⚪ 恭喜白棋获胜！")
        
        self.player_indicator.config(text="游戏已结束，点击重新开始继续对战")
        self.flash_victory()
        
    def flash_victory(self):
        """胜利信息闪烁效果"""
        colors = ['#D2691E', '#B22222', '#8B0000', '#B22222', '#D2691E']
        
        def flash(i=0):
            if i < len(colors) and self.game_over:
                self.victory_frame.config(bg=colors[i])
                self.victory_label.config(bg=colors[i])
                self.window.after(150, lambda: flash(i+1))
            else:
                self.victory_frame.config(bg='#D2691E')
                self.victory_label.config(bg='#D2691E')
                
        flash()
        
    def hide_victory_message(self):
        """隐藏胜利信息"""
        self.victory_frame.pack_forget()
        
    def show_menu(self):
        """显示主菜单"""
        self.canvas.delete("all")
        self.draw_board()
        self.game_mode = None
        self.game_over = True
        self.winner = None
        self.last_move = None
        self.difficulty_frame.pack_forget()
        self.hide_victory_message()
        self.status_label.config(text="⚫ 黑棋先手")
        self.player_indicator.config(text="请选择游戏模式")
        self.restart_btn.config(state=tk.DISABLED)
        
    def start_pvp(self):
        """开始玩家对战模式"""
        self.game_mode = 'pvp'
        self.difficulty_frame.pack_forget()
        self.init_game()
        self.hide_victory_message()
        self.status_label.config(text="👥 玩家对战模式")
        self.player_indicator.config(text="⚫ 黑棋先手")
        self.restart_btn.config(state=tk.NORMAL)
        
    def start_pvc(self):
        """开始人机对战模式"""
        self.game_mode = 'pvc'
        self.difficulty_frame.pack(fill=tk.X, pady=20)
        self.difficulty = self.difficulty_var.get()
        self.init_game()
        self.hide_victory_message()
        self.status_label.config(text="🤖 人机对战模式")
        self.player_indicator.config(text="⚫ 黑棋先手")
        self.restart_btn.config(state=tk.NORMAL)
        
    def init_game(self):
        """初始化游戏"""
        self.board = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.canvas.delete("all")
        self.draw_board()
        self.hide_victory_message()
        self.update_status()
        
    def draw_board(self):
        """绘制棋盘"""
        # 绘制网格
        for i in range(self.BOARD_SIZE):
            x1 = self.MARGIN
            y1 = self.MARGIN + i * self.CELL_SIZE
            x2 = self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL_SIZE
            y2 = y1
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill='black')
            
            x1 = self.MARGIN + i * self.CELL_SIZE
            y1 = self.MARGIN
            x2 = x1
            y2 = self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL_SIZE
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill='black')
        
        # 绘制星位
        star_points = [3, 7, 11]
        for i in star_points:
            for j in star_points:
                x = self.MARGIN + i * self.CELL_SIZE
                y = self.MARGIN + j * self.CELL_SIZE
                self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='black')
        
        # 绘制边框
        self.canvas.create_rectangle(self.MARGIN-2, self.MARGIN-2,
                                    self.MARGIN + (self.BOARD_SIZE-1)*self.CELL_SIZE + 2,
                                    self.MARGIN + (self.BOARD_SIZE-1)*self.CELL_SIZE + 2,
                                    width=3, outline='#8B4513')
        
    def on_mouse_move(self, event):
        """鼠标移动事件 - 显示预览"""
        if self.game_over or not self.game_mode:
            return
            
        self.canvas.delete("preview")
        
        x = round((event.x - self.MARGIN) / self.CELL_SIZE)
        y = round((event.y - self.MARGIN) / self.CELL_SIZE)
        
        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            if self.board[y][x] == 0:
                cx = self.MARGIN + x * self.CELL_SIZE
                cy = self.MARGIN + y * self.CELL_SIZE
                
                color = 'gray'
                self.canvas.create_oval(cx - self.PIECE_RADIUS, cy - self.PIECE_RADIUS,
                                       cx + self.PIECE_RADIUS, cy + self.PIECE_RADIUS,
                                       fill=color, outline='', stipple='gray50',
                                       tags="preview")
        
    def on_click(self, event):
        """鼠标点击事件"""
        if self.game_over or not self.game_mode:
            return
            
        x = round((event.x - self.MARGIN) / self.CELL_SIZE)
        y = round((event.y - self.MARGIN) / self.CELL_SIZE)
        
        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            if self.make_move(x, y):
                if not self.game_over and self.game_mode == 'pvc' and self.current_player == 2:
                    self.window.after(200, self.ai_move)
                    
    def make_move(self, x, y):
        """执行落子"""
        if self.board[y][x] != 0:
            return False
            
        # 先清除之前的最后落子标记
        self.clear_last_move_marker()
        
        # 落子
        self.board[y][x] = self.current_player
        self.last_move = (x, y)  # 记录最后落子位置
        self.draw_piece(x, y, self.current_player)
        
        if self.check_win(x, y, self.current_player):
            self.game_over = True
            self.winner = self.current_player
            self.show_win_effect(x, y)
            self.show_victory_message(self.current_player, is_draw=False)
            return True
            
        if not np.any(self.board == 0):
            self.game_over = True
            self.winner = None
            self.show_victory_message(None, is_draw=True)
            return True
            
        self.current_player = 3 - self.current_player
        self.update_status()
        return True
        
    def clear_last_move_marker(self):
        """清除最后落子标记"""
        if self.last_move:
            x, y = self.last_move
            # 重新绘制该位置的棋子（不带红点）
            player = self.board[y][x]
            if player != 0:  # 如果该位置有棋子
                self.draw_piece(x, y, player, with_marker=False)
        
    def draw_piece(self, x, y, player, with_marker=True):
        """绘制棋子
        with_marker: 是否显示最后落子标记
        """
        cx = self.MARGIN + x * self.CELL_SIZE
        cy = self.MARGIN + y * self.CELL_SIZE
        
        # 删除该位置原有的所有图形
        self.canvas.delete(f"piece_{x}_{y}")
        
        # 阴影
        self.canvas.create_oval(cx - self.PIECE_RADIUS + 2, cy - self.PIECE_RADIUS + 2,
                               cx + self.PIECE_RADIUS + 2, cy + self.PIECE_RADIUS + 2,
                               fill='#444444', outline='', tags=f"piece_{x}_{y}")
        
        # 棋子
        color = '#222222' if player == 1 else 'white'
        outline_color = '#666666' if player == 1 else '#CCCCCC'
        
        self.canvas.create_oval(cx - self.PIECE_RADIUS, cy - self.PIECE_RADIUS,
                               cx + self.PIECE_RADIUS, cy + self.PIECE_RADIUS,
                               fill=color, outline=outline_color, width=2,
                               tags=f"piece_{x}_{y}")
        
        # 高光
        if player == 1:
            self.canvas.create_oval(cx - 5, cy - 5, cx - 2, cy - 2, 
                                   fill='#666666', outline='', tags=f"piece_{x}_{y}")
        else:
            self.canvas.create_oval(cx - 5, cy - 5, cx - 2, cy - 2,
                                   fill='#EEEEEE', outline='', tags=f"piece_{x}_{y}")
        
        # 最后落子标记 - 始终显示，包括游戏结束后
        if with_marker and self.last_move == (x, y):
            # 绘制一个醒目的红点
            self.canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6,
                                   fill='#FF4444', outline='white', width=2,
                                   tags=f"piece_{x}_{y}_marker")
            # 添加光晕效果
            self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10,
                                   outline='#FF8888', width=2, dash=(2, 2),
                                   tags=f"piece_{x}_{y}_marker")
        
    def show_win_effect(self, win_x, win_y):
        """显示胜利特效"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        player = self.board[win_y][win_x]
        
        for dx, dy in directions:
            count = 1
            positions = [(win_x, win_y)]
            
            for step in range(1, 5):
                nx, ny = win_x + dx * step, win_y + dy * step
                if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                    if self.board[ny][nx] == player:
                        count += 1
                        positions.append((nx, ny))
                    else:
                        break
                else:
                    break
            
            for step in range(1, 5):
                nx, ny = win_x - dx * step, win_y - dy * step
                if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                    if self.board[ny][nx] == player:
                        count += 1
                        positions.append((nx, ny))
                    else:
                        break
                else:
                    break
            
            if count >= 5:
                for x, y in positions[:5]:
                    cx = self.MARGIN + x * self.CELL_SIZE
                    cy = self.MARGIN + y * self.CELL_SIZE
                    self.canvas.create_oval(cx - self.PIECE_RADIUS - 2, 
                                           cy - self.PIECE_RADIUS - 2,
                                           cx + self.PIECE_RADIUS + 2, 
                                           cy + self.PIECE_RADIUS + 2,
                                           outline='gold', width=4, tags="win_effect")
                break
        
    def update_status(self):
        """更新状态显示"""
        if self.game_over:
            return
            
        player_str = "⚫ 黑棋" if self.current_player == 1 else "⚪ 白棋"
        self.status_label.config(text=f"{player_str} 回合")
        self.player_indicator.config(text=f"当前模式: {'玩家对战' if self.game_mode == 'pvp' else '人机对战'}")
        
    def check_win(self, x, y, player):
        """检查是否获胜"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            for step in range(1, 5):
                nx, ny = x + dx * step, y + dy * step
                if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                    if self.board[ny][nx] == player:
                        count += 1
                    else:
                        break
                else:
                    break
                    
            for step in range(1, 5):
                nx, ny = x - dx * step, y - dy * step
                if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                    if self.board[ny][nx] == player:
                        count += 1
                    else:
                        break
                else:
                    break
                    
            if count >= 5:
                return True
                
        return False
        
    def ai_move(self):
        """AI走棋"""
        if self.game_over or self.current_player != 2:
            return
            
        difficulty = self.difficulty_var.get()
        
        if difficulty == "easy":
            x, y = self.ai_move_easy()
        elif difficulty == "medium":
            x, y = self.ai_move_medium()
        else:
            x, y = self.ai_move_hard()
            
        if x is not None and y is not None:
            self.make_move(x, y)
        
    def ai_move_easy(self):
        """简单难度AI"""
        empty_positions = [(x, y) for y in range(self.BOARD_SIZE) 
                          for x in range(self.BOARD_SIZE) if self.board[y][x] == 0]
        if empty_positions:
            return random.choice(empty_positions)
        return None, None
        
    def ai_move_medium(self):
        """中等难度AI"""
        best_score = -1
        best_move = None
        
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self.board[y][x] == 0:
                    score = self.evaluate_position(x, y, 2) * 1.5
                    score += self.evaluate_position(x, y, 1) * 1.0
                    
                    center = self.BOARD_SIZE // 2
                    distance = abs(x - center) + abs(y - center)
                    score += (self.BOARD_SIZE - distance) * 0.5
                    
                    if score > best_score:
                        best_score = score
                        best_move = (x, y)
                        
        return best_move if best_move else (None, None)
        
    def ai_move_hard(self):
        """困难难度AI"""
        best_score = -float('inf')
        best_move = None
        
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self.board[y][x] == 0:
                    self.board[y][x] = 2
                    score = self.minimax(2, -float('inf'), float('inf'), False)
                    self.board[y][x] = 0
                    
                    if score > best_score:
                        best_score = score
                        best_move = (x, y)
                        
        return best_move if best_move else self.ai_move_medium()
        
    def minimax(self, depth, alpha, beta, is_maximizing):
        """极小极大搜索算法"""
        if depth == 0:
            return self.evaluate_board()
            
        if is_maximizing:
            max_eval = -float('inf')
            for y in range(self.BOARD_SIZE):
                for x in range(self.BOARD_SIZE):
                    if self.board[y][x] == 0:
                        self.board[y][x] = 2
                        eval = self.minimax(depth - 1, alpha, beta, False)
                        self.board[y][x] = 0
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for y in range(self.BOARD_SIZE):
                for x in range(self.BOARD_SIZE):
                    if self.board[y][x] == 0:
                        self.board[y][x] = 1
                        eval = self.minimax(depth - 1, alpha, beta, True)
                        self.board[y][x] = 0
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return min_eval
            
    def evaluate_board(self):
        """评估整个棋盘"""
        score = 0
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self.board[y][x] == 2:
                    score += self.evaluate_position(x, y, 2)
                elif self.board[y][x] == 1:
                    score -= self.evaluate_position(x, y, 1) * 0.8
        return score
        
    def evaluate_position(self, x, y, player):
        """评估位置分数"""
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            block_left = False
            block_right = False
            
            for step in range(1, 5):
                nx, ny = x + dx * step, y + dy * step
                if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                    if self.board[ny][nx] == player:
                        count += 1
                    elif self.board[ny][nx] == 0:
                        break
                    else:
                        block_right = True
                        break
                else:
                    block_right = True
                    break
                    
            for step in range(1, 5):
                nx, ny = x - dx * step, y - dy * step
                if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                    if self.board[ny][nx] == player:
                        count += 1
                    elif self.board[ny][nx] == 0:
                        break
                    else:
                        block_left = True
                        break
                else:
                    block_left = True
                    break
            
            if count >= 5:
                score += 100000
            elif count == 4:
                if not (block_left and block_right):
                    score += 10000
                else:
                    score += 100
            elif count == 3:
                if not (block_left and block_right):
                    score += 1000
                else:
                    score += 50
            elif count == 2:
                if not (block_left and block_right):
                    score += 100
                else:
                    score += 10
            elif count == 1:
                score += 1
                
        return score
        
    def restart_game(self):
        """重新开始游戏"""
        if self.game_mode == 'pvp':
            self.start_pvp()
        elif self.game_mode == 'pvc':
            self.start_pvc()
            
    def run(self):
        """运行游戏"""
        self.window.mainloop()

if __name__ == "__main__":
    game = Gomoku()
    game.run()