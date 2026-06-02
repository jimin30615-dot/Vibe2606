import random
import tkinter as tk

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 20
BULLET_WIDTH = 6
BULLET_HEIGHT = 14
ENEMY_SIZE = 40
ENEMY_SPEED = 4
BULLET_SPEED = 14
SPAWN_INTERVAL = 1200
GAME_LOOP_INTERVAL = 25


class ShootingGame:
    def __init__(self, root):
        self.root = root
        self.root.title('사격 게임')
        self.root.resizable(False, False)

        self.score = 0
        self.game_over = False
        self.bullets = []
        self.enemies = []
        self.enemy_spawn_job = None
        self.game_loop_job = None
        self.enemy_count = 0
        self.player_tag = 'player'

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='#0b0b2d')
        self.canvas.pack()

        self.score_text = self.canvas.create_text(
            10, 10, anchor='nw', text='점수: 0', fill='white', font=('Arial', 18, 'bold')
        )
        self.info_text = self.canvas.create_text(
            WINDOW_WIDTH - 10, 10, anchor='ne',
            text='← → : 이동    스페이스 : 발사', fill='#cccccc', font=('Arial', 12)
        )

        self.player = self.player_tag
        self.reset_player()

        self.root.bind('<Left>', lambda event: self.move_player(-1))
        self.root.bind('<Right>', lambda event: self.move_player(1))
        self.root.bind('<space>', lambda event: self.fire_bullet())

        self.start_game()

    def reset_player(self):
        self.canvas.delete(self.player_tag)
        x = (WINDOW_WIDTH - PLAYER_WIDTH) / 2
        y = WINDOW_HEIGHT - PLAYER_HEIGHT - 20
        head_size = 18
        body_width = 24
        body_height = 32
        head_x = x + (PLAYER_WIDTH - head_size) / 2
        head_y = y - head_size - 4
        body_x = x + (PLAYER_WIDTH - body_width) / 2
        body_y = y

        self.canvas.create_oval(
            head_x, head_y, head_x + head_size, head_y + head_size,
            fill='#f5f6fa', outline='#dcdde1', tags=self.player_tag
        )
        self.canvas.create_rectangle(
            body_x, body_y, body_x + body_width, body_y + body_height,
            fill='#3ae374', outline='#2ed573', tags=self.player_tag
        )
        self.canvas.create_line(
            body_x, body_y + 10, body_x + body_width, body_y + 10,
            fill='#2f3542', width=2, tags=self.player_tag
        )

    def start_game(self):
        self.score = 0
        self.game_over = False
        self.bullets.clear()
        self.enemies.clear()
        self.enemy_count = 0
        self.canvas.delete('bullet')
        self.canvas.delete('enemy')
        self.canvas.delete('gameover')
        self.canvas.itemconfigure(self.score_text, text='점수: 0')
        self.reset_player()
        self.spawn_enemy()
        self.game_loop()

    def move_player(self, direction):
        if self.game_over:
            return
        coords = self.canvas.bbox(self.player_tag)
        if not coords:
            return
        x1, _, x2, _ = coords
        dx = 20 * direction
        if x1 + dx < 0:
            dx = -x1
        if x2 + dx > WINDOW_WIDTH:
            dx = WINDOW_WIDTH - x2
        self.canvas.move(self.player_tag, dx, 0)

    def fire_bullet(self):
        if self.game_over:
            return
        player_coords = self.canvas.bbox(self.player_tag)
        if not player_coords:
            return
        x1, y1, x2, _ = player_coords
        bullet_x = (x1 + x2) / 2 - BULLET_WIDTH / 2
        bullet_y = y1 - BULLET_HEIGHT
        bullet_id = self.canvas.create_rectangle(
            bullet_x, bullet_y, bullet_x + BULLET_WIDTH, bullet_y + BULLET_HEIGHT,
            fill='#ffffff', outline='#ffffff', tags='bullet'
        )
        self.bullets.append(bullet_id)

    def spawn_enemy(self):
        if self.game_over:
            return
        x = random.randint(0, WINDOW_WIDTH - ENEMY_SIZE)
        tag = f'enemy{self.enemy_count}'
        head_d = 16
        body_w = 20
        body_h = 28
        head_x = x + (ENEMY_SIZE - head_d) / 2
        head_y = 4
        body_x = x + (ENEMY_SIZE - body_w) / 2
        body_y = head_y + head_d

        self.canvas.create_oval(
            head_x, head_y, head_x + head_d, head_y + head_d,
            fill='#ff6b81', outline='#ff4757', tags=(tag, 'enemy')
        )
        self.canvas.create_rectangle(
            body_x, body_y, body_x + body_w, body_y + body_h,
            fill='#ff3f34', outline='#ff793f', tags=(tag, 'enemy')
        )
        self.canvas.create_line(
            body_x - 6, body_y + 10, body_x + body_w + 6, body_y + 10,
            fill='#2f3542', width=2, tags=(tag, 'enemy')
        )
        self.enemies.append(tag)
        self.enemy_count += 1
        self.enemy_spawn_job = self.root.after(SPAWN_INTERVAL, self.spawn_enemy)

    def game_loop(self):
        if self.game_over:
            return
        self.move_bullets()
        self.move_enemies()
        self.check_collisions()
        self.game_loop_job = self.root.after(GAME_LOOP_INTERVAL, self.game_loop)

    def move_bullets(self):
        for bullet_id in self.bullets[:]:
            self.canvas.move(bullet_id, 0, -BULLET_SPEED)
            _, y1, _, y2 = self.canvas.coords(bullet_id)
            if y2 < 0:
                self.canvas.delete(bullet_id)
                self.bullets.remove(bullet_id)

    def move_enemies(self):
        for enemy_id in self.enemies[:]:
            self.canvas.move(enemy_id, 0, ENEMY_SPEED)
            enemy_bbox = self.canvas.bbox(enemy_id)
            if enemy_bbox and enemy_bbox[3] >= WINDOW_HEIGHT:
                self.end_game()
                return

    def check_collisions(self):
        for bullet_id in self.bullets[:]:
            bullet_coords = self.canvas.bbox(bullet_id)
            if not bullet_coords:
                continue
            hits = self.canvas.find_overlapping(*bullet_coords)
            for hit_id in hits:
                if 'enemy' in self.canvas.gettags(hit_id):
                    enemy_tags = [tag for tag in self.canvas.gettags(hit_id) if tag.startswith('enemy') and tag != 'enemy']
                    if enemy_tags:
                        enemy_tag = enemy_tags[0]
                        self.canvas.delete(enemy_tag)
                        if enemy_tag in self.enemies:
                            self.enemies.remove(enemy_tag)
                    self.canvas.delete(bullet_id)
                    if bullet_id in self.bullets:
                        self.bullets.remove(bullet_id)
                    self.add_score(10)
                    break

        player_coords = self.canvas.bbox(self.player)
        for enemy_id in self.enemies:
            enemy_coords = self.canvas.bbox(enemy_id)
            if enemy_coords and self.overlap(player_coords, enemy_coords):
                self.end_game()
                return

    def overlap(self, rect1, rect2):
        x1, y1, x2, y2 = rect1
        a1, b1, a2, b2 = rect2
        return x1 < a2 and x2 > a1 and y1 < b2 and y2 > b1

    def add_score(self, points):
        self.score += points
        self.canvas.itemconfigure(self.score_text, text=f'점수: {self.score}')

    def end_game(self):
        self.game_over = True
        if self.enemy_spawn_job is not None:
            self.root.after_cancel(self.enemy_spawn_job)
            self.enemy_spawn_job = None
        if self.game_loop_job is not None:
            self.root.after_cancel(self.game_loop_job)
            self.game_loop_job = None

        self.canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 - 30,
            text='게임 오버', font=('Arial', 36, 'bold'), fill='#ff4757', tags='gameover'
        )
        self.canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 30,
            text='R 키를 눌러 다시 시작', font=('Arial', 18), fill='white', tags='gameover'
        )
        self.root.bind('<r>', lambda event: self.start_game())


if __name__ == '__main__':
    root = tk.Tk()
    game = ShootingGame(root)
    root.mainloop()
