import tkinter as tk
from tkinter import font, messagebox
import random
import threading
import time

# 게임 설정
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30

# 테트로미노 정의
TETROMINOS = {
    'I': {
        'shape': [[1, 1, 1, 1]],
        'color': '#00f0f0'
    },
    'O': {
        'shape': [[1, 1], [1, 1]],
        'color': '#f0f000'
    },
    'T': {
        'shape': [[0, 1, 0], [1, 1, 1]],
        'color': '#a000f0'
    },
    'S': {
        'shape': [[0, 1, 1], [1, 1, 0]],
        'color': '#00f000'
    },
    'Z': {
        'shape': [[1, 1, 0], [0, 1, 1]],
        'color': '#f00000'
    },
    'J': {
        'shape': [[1, 0, 0], [1, 1, 1]],
        'color': '#0000f0'
    },
    'L': {
        'shape': [[0, 0, 1], [1, 1, 1]],
        'color': '#f0a000'
    }
}


class TetrisGame:
    def __init__(self, root):
        self.root = root
        self.root.title('테트리스 게임')
        self.root.geometry('800x700')
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)

        # 게임 상태
        self.board = []
        self.current_block = None
        self.next_block_type = None
        self.game_running = False
        self.game_paused = False
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_speed = 1000
        self.game_loop_id = None

        # UI 구성
        self.setup_ui()
        self.init_board()
        self.draw_board()

    def setup_ui(self):
        """UI 레이아웃 설정"""
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 제목
        title_label = tk.Label(main_frame, text='🎮 테트리스', font=('Arial', 24, 'bold'), 
                               fg='white', bg='#1a1a2e')
        title_label.pack(pady=10)

        # 게임 콘텐츠 프레임
        content_frame = tk.Frame(main_frame, bg='#1a1a2e')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 게임 보드
        self.canvas = tk.Canvas(content_frame, width=BOARD_WIDTH * BLOCK_SIZE + 20,
                                height=BOARD_HEIGHT * BLOCK_SIZE + 20, bg='#2a2a4a',
                                highlightthickness=2, highlightbackground='#16c784')
        self.canvas.pack(side=tk.LEFT, padx=20)

        # 정보 패널
        info_frame = tk.Frame(content_frame, bg='#1a1a2e')
        info_frame.pack(side=tk.RIGHT, padx=20, fill=tk.BOTH, expand=True)

        # 점수
        score_label = tk.Label(info_frame, text='점수', font=('Arial', 12, 'bold'),
                               fg='#16c784', bg='#1a1a2e')
        score_label.pack(pady=(20, 5))
        self.score_var = tk.StringVar(value='0')
        self.score_display = tk.Label(info_frame, textvariable=self.score_var,
                                      font=('Arial', 20, 'bold'), fg='white', bg='#1a1a2e')
        self.score_display.pack()

        # 레벨
        level_label = tk.Label(info_frame, text='레벨', font=('Arial', 12, 'bold'),
                               fg='#16c784', bg='#1a1a2e')
        level_label.pack(pady=(20, 5))
        self.level_var = tk.StringVar(value='1')
        self.level_display = tk.Label(info_frame, textvariable=self.level_var,
                                      font=('Arial', 20, 'bold'), fg='white', bg='#1a1a2e')
        self.level_display.pack()

        # 라인
        lines_label = tk.Label(info_frame, text='라인', font=('Arial', 12, 'bold'),
                               fg='#16c784', bg='#1a1a2e')
        lines_label.pack(pady=(20, 5))
        self.lines_var = tk.StringVar(value='0')
        self.lines_display = tk.Label(info_frame, textvariable=self.lines_var,
                                      font=('Arial', 20, 'bold'), fg='white', bg='#1a1a2e')
        self.lines_display.pack()

        # 다음 블록
        next_label = tk.Label(info_frame, text='다음 블록', font=('Arial', 12, 'bold'),
                              fg='#16c784', bg='#1a1a2e')
        next_label.pack(pady=(20, 5))
        self.next_canvas = tk.Canvas(info_frame, width=4 * BLOCK_SIZE - 20, 
                                     height=4 * BLOCK_SIZE - 20, bg='#2a2a4a',
                                     highlightthickness=1, highlightbackground='#16c784')
        self.next_canvas.pack(pady=10)

        # 버튼 프레임
        button_frame = tk.Frame(info_frame, bg='#1a1a2e')
        button_frame.pack(pady=20, fill=tk.X)

        self.start_btn = tk.Button(button_frame, text='시작', font=('Arial', 10, 'bold'),
                                   command=self.toggle_game, bg='#16c784', fg='white',
                                   padx=20, pady=10)
        self.start_btn.pack(pady=5, fill=tk.X)

        self.pause_btn = tk.Button(button_frame, text='일시정지', font=('Arial', 10, 'bold'),
                                   command=self.toggle_pause, bg='#16c784', fg='white',
                                   padx=20, pady=10, state=tk.DISABLED)
        self.pause_btn.pack(pady=5, fill=tk.X)

        reset_btn = tk.Button(button_frame, text='리셋', font=('Arial', 10, 'bold'),
                              command=self.reset_game, bg='#16c784', fg='white',
                              padx=20, pady=10)
        reset_btn.pack(pady=5, fill=tk.X)

        # 조작 설명
        info_text = tk.Label(info_frame, text='조작 방법:\n← → : 좌우 이동\n↑ : 회전\n↓ : 빠른 낙하\n스페이스 : 즉시 낙하',
                             font=('Arial', 9), fg='#ccc', bg='#1a1a2e', justify=tk.LEFT)
        info_text.pack(pady=20)

        # 키보드 이벤트 바인딩
        self.root.bind('<Left>', lambda e: self.move_block(-1))
        self.root.bind('<Right>', lambda e: self.move_block(1))
        self.root.bind('<Up>', lambda e: self.rotate_block())
        self.root.bind('<Down>', lambda e: self.drop_block())
        self.root.bind('<space>', lambda e: self.hard_drop())

    def init_board(self):
        """보드 초기화"""
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

    def get_random_block(self):
        """랜덤 블록 타입 반환"""
        return random.choice(list(TETROMINOS.keys()))

    def create_new_block(self):
        """새로운 블록 생성"""
        if not self.next_block_type:
            self.next_block_type = self.get_random_block()

        block_type = self.next_block_type
        self.next_block_type = self.get_random_block()

        tetromino = TETROMINOS[block_type]
        self.current_block = {
            'shape': [row[:] for row in tetromino['shape']],
            'color': tetromino['color'],
            'row': 0,
            'col': (BOARD_WIDTH - len(tetromino['shape'][0])) // 2
        }

        self.draw_next_block()

        if self.is_colliding():
            self.end_game()

    def is_colliding(self, block=None):
        """충돌 검사"""
        if block is None:
            block = self.current_block

        if block is None:
            return False

        for row in range(len(block['shape'])):
            for col in range(len(block['shape'][row])):
                if block['shape'][row][col]:
                    board_row = block['row'] + row
                    board_col = block['col'] + col

                    if board_row >= BOARD_HEIGHT or board_col < 0 or board_col >= BOARD_WIDTH:
                        return True

                    if board_row >= 0 and self.board[board_row][board_col]:
                        return True

        return False

    def place_block(self):
        """블록 배치"""
        for row in range(len(self.current_block['shape'])):
            for col in range(len(self.current_block['shape'][row])):
                if self.current_block['shape'][row][col]:
                    board_row = self.current_block['row'] + row
                    board_col = self.current_block['col'] + col

                    if 0 <= board_row < BOARD_HEIGHT and 0 <= board_col < BOARD_WIDTH:
                        self.board[board_row][board_col] = 1

        self.check_lines()
        self.create_new_block()

    def check_lines(self):
        """라인 체크 및 제거"""
        completed_lines = 0
        row = BOARD_HEIGHT - 1

        while row >= 0:
            if all(self.board[row]):
                self.board.pop(row)
                self.board.insert(0, [0] * BOARD_WIDTH)
                completed_lines += 1
            else:
                row -= 1

        if completed_lines > 0:
            self.lines += completed_lines
            self.score += completed_lines * completed_lines * 100
            self.level = (self.lines // 10) + 1
            self.game_speed = max(200, 1000 - (self.level - 1) * 50)

            self.score_var.set(str(self.score))
            self.lines_var.set(str(self.lines))
            self.level_var.set(str(self.level))

    def move_block(self, direction):
        """블록 이동"""
        if not self.current_block or self.game_paused or not self.game_running:
            return

        new_block = {
            'shape': self.current_block['shape'],
            'color': self.current_block['color'],
            'row': self.current_block['row'],
            'col': self.current_block['col'] + direction
        }

        if not self.is_colliding(new_block):
            self.current_block['col'] = new_block['col']
            self.draw_board()

    def rotate_block(self):
        """블록 회전"""
        if not self.current_block or self.game_paused or not self.game_running:
            return

        # 90도 시계방향 회전
        rotated_shape = [list(row) for row in zip(*self.current_block['shape'][::-1])]

        new_block = {
            'shape': rotated_shape,
            'color': self.current_block['color'],
            'row': self.current_block['row'],
            'col': self.current_block['col']
        }

        if not self.is_colliding(new_block):
            self.current_block['shape'] = rotated_shape
            self.draw_board()

    def drop_block(self):
        """블록 낙하"""
        if not self.current_block or self.game_paused or not self.game_running:
            return

        new_block = {
            'shape': self.current_block['shape'],
            'color': self.current_block['color'],
            'row': self.current_block['row'] + 1,
            'col': self.current_block['col']
        }

        if self.is_colliding(new_block):
            self.place_block()
            self.draw_board()
        else:
            self.current_block['row'] += 1
            self.draw_board()

    def hard_drop(self):
        """즉시 낙하"""
        if not self.current_block or self.game_paused or not self.game_running:
            return

        while True:
            test_block = {
                'shape': self.current_block['shape'],
                'color': self.current_block['color'],
                'row': self.current_block['row'] + 1,
                'col': self.current_block['col']
            }
            if self.is_colliding(test_block):
                break
            self.current_block['row'] += 1

        self.place_block()
        self.draw_board()

    def draw_board(self):
        """보드 그리기"""
        self.canvas.delete('all')

        # 배경
        self.canvas.create_rectangle(10, 10, BOARD_WIDTH * BLOCK_SIZE + 10,
                                     BOARD_HEIGHT * BLOCK_SIZE + 10, fill='#1a1a2e')

        # 보드 그리드
        for row in range(BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                x = 10 + col * BLOCK_SIZE
                y = 10 + row * BLOCK_SIZE

                if self.board[row][col]:
                    self.canvas.create_rectangle(x, y, x + BLOCK_SIZE - 1, y + BLOCK_SIZE - 1,
                                                fill='#16c784', outline='#0ecb81')
                else:
                    self.canvas.create_rectangle(x, y, x + BLOCK_SIZE - 1, y + BLOCK_SIZE - 1,
                                                fill='#2a2a4a', outline='#3a3a5a')

        # 현재 블록 그리기
        if self.current_block:
            for row in range(len(self.current_block['shape'])):
                for col in range(len(self.current_block['shape'][row])):
                    if self.current_block['shape'][row][col]:
                        board_row = self.current_block['row'] + row
                        board_col = self.current_block['col'] + col

                        if 0 <= board_row < BOARD_HEIGHT and 0 <= board_col < BOARD_WIDTH:
                            x = 10 + board_col * BLOCK_SIZE
                            y = 10 + board_row * BLOCK_SIZE
                            self.canvas.create_rectangle(x, y, x + BLOCK_SIZE - 1, y + BLOCK_SIZE - 1,
                                                        fill=self.current_block['color'],
                                                        outline='#ffffff')

    def draw_next_block(self):
        """다음 블록 미리보기 그리기"""
        self.next_canvas.delete('all')

        if self.next_block_type:
            tetromino = TETROMINOS[self.next_block_type]
            shape = tetromino['shape']
            color = tetromino['color']

            block_size = 25
            for row in range(4):
                for col in range(4):
                    if row < len(shape) and col < len(shape[row]) and shape[row][col]:
                        x = col * block_size
                        y = row * block_size
                        self.next_canvas.create_rectangle(x, y, x + block_size - 1, y + block_size - 1,
                                                         fill=color, outline='#ffffff')

    def game_loop(self):
        """게임 루프"""
        if not self.game_running or self.game_paused:
            return

        self.drop_block()
        self.game_loop_id = self.root.after(self.game_speed, self.game_loop)

    def toggle_game(self):
        """게임 시작/중지"""
        if not self.game_running:
            self.game_running = True
            self.game_paused = False
            self.init_board()
            self.create_new_block()
            self.draw_board()
            self.start_btn.config(text='중지')
            self.pause_btn.config(state=tk.NORMAL)
            self.game_loop()
        else:
            self.game_running = False
            self.game_paused = False
            if self.game_loop_id:
                self.root.after_cancel(self.game_loop_id)
            self.start_btn.config(text='시작')
            self.pause_btn.config(state=tk.DISABLED, text='일시정지')

    def toggle_pause(self):
        """일시정지/계속"""
        self.game_paused = not self.game_paused
        self.pause_btn.config(text='계속' if self.game_paused else '일시정지')

    def reset_game(self):
        """게임 리셋"""
        self.game_running = False
        self.game_paused = False
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_speed = 1000
        self.current_block = None
        self.next_block_type = None

        if self.game_loop_id:
            self.root.after_cancel(self.game_loop_id)

        self.start_btn.config(text='시작')
        self.pause_btn.config(state=tk.DISABLED, text='일시정지')
        self.score_var.set('0')
        self.lines_var.set('0')
        self.level_var.set('1')

        self.init_board()
        self.draw_board()
        self.draw_next_block()

    def end_game(self):
        """게임 오버"""
        self.game_running = False
        if self.game_loop_id:
            self.root.after_cancel(self.game_loop_id)

        messagebox.showinfo('게임 오버', f'최종 점수: {self.score}')

        self.start_btn.config(text='시작')
        self.pause_btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    game = TetrisGame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
