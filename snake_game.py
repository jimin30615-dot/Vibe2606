#pip install pygame

import pygame
import random
from enum import Enum
from typing import List, Tuple, Optional


class Direction(Enum):
    """뱀의 이동 방향을 정의하는 열거형"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Snake:
    """뱀을 관리하는 클래스"""
    def __init__(self, grid_width: int, grid_height: int, cell_size: int, 
                 start_x: Optional[int] = None, start_y: Optional[int] = None):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        
        # 뱀의 초기 위치
        if start_x is None:
            start_x = grid_width // 2
        if start_y is None:
            start_y = grid_height // 2
            
        self.body: List[Tuple[int, int]] = [(start_x, start_y),
                                            (start_x - 1, start_y),
                                            (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
    
    def change_direction(self, direction: Direction):
        """뱀의 방향을 변경 (반대 방향 불가)"""
        # 현재 방향의 반대 방향으로 변경 불가
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if direction != opposite.get(self.direction):
            self.next_direction = direction
    
    def move(self) -> bool:
        """뱀을 한 칸 이동 (충돌 감지 반환)"""
        self.direction = self.next_direction
        
        # 머리의 현재 위치
        head_x, head_y = self.body[0]
        
        # 새로운 머리 위치
        dx, dy = self.direction.value
        new_head_x = head_x + dx
        new_head_y = head_y + dy
        
        # 벽 충돌 감지
        if (new_head_x < 0 or new_head_x >= self.grid_width or
            new_head_y < 0 or new_head_y >= self.grid_height):
            return False
        
        # 새로운 위치를 머리로 추가
        self.body.insert(0, (new_head_x, new_head_y))
        
        # 몸과의 충돌 감지
        if (new_head_x, new_head_y) in self.body[1:]:
            return False
        
        return True
    
    def eat_food(self):
        """음식을 먹을 때 (꼬리를 자르지 않음)"""
        pass  # 음식 먹기는 move에서 꼬리를 제거하지 않음으로 처리
    
    def grow(self):
        """뱀이 성장 (move 후에 호출되어야 함)"""
        # move에서 이미 body가 추가되었으므로 여기서는 아무것도 하지 않음
        pass
    
    def get_head(self) -> Tuple[int, int]:
        """뱀의 머리 위치 반환"""
        return self.body[0]
    
    def remove_tail(self):
        """꼬리를 제거"""
        if len(self.body) > 0:
            self.body.pop()
    
    def draw(self, screen: pygame.Surface, cell_size: int, color_head=(0, 255, 0),
             color_body=(0, 200, 0)):
        """뱀을 화면에 그리기"""
        # 머리 그리기
        head_x, head_y = self.body[0]
        pygame.draw.rect(screen, color_head,
                        (head_x * cell_size, head_y * cell_size,
                         cell_size, cell_size))
        
        # 몸 그리기
        for segment in self.body[1:]:
            x, y = segment
            pygame.draw.rect(screen, color_body,
                           (x * cell_size, y * cell_size,
                            cell_size, cell_size))


class Food:
    """음식을 관리하는 클래스"""
    def __init__(self, grid_width: int, grid_height: int, food_count: int = 3):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.food_count = food_count
        self.positions: List[Tuple[int, int]] = []
        self.spawn_initial()
    
    def spawn_initial(self):
        """초기 음식들 생성"""
        self.positions = []
        for _ in range(self.food_count):
            self.spawn_new()
    
    def spawn_new(self, occupied: List[Tuple[int, int]] = None):
        """새로운 음식 위치 생성"""
        if occupied is None:
            occupied = []
        
        occupied = occupied + self.positions  # 기존 음식들도 제외
        
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in occupied:
                self.positions.append((x, y))
                break
    
    def remove_food(self, position: Tuple[int, int]):
        """특정 위치의 음식 제거"""
        if position in self.positions:
            self.positions.remove(position)
    
    def draw(self, screen: pygame.Surface, cell_size: int, color=(255, 255, 0)):
        """음식을 화면에 그리기"""
        for x, y in self.positions:
            pygame.draw.rect(screen, color,
                            (x * cell_size, y * cell_size,
                             cell_size, cell_size))


class MultiSnakeGame:
    """2마리 뱀이 경쟁하는 게임을 관리하는 클래스"""
    def __init__(self, width: int = 800, height: int = 600, cell_size: int = 20):
        pygame.init()
        
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("뱀 게임 - 2P (플레이어 vs AI)")
        
        self.clock = pygame.time.Clock()
        self.fps = 10
        
        # 게임 객체 초기화
        # 플레이어 1: 왼쪽 시작
        self.player_snake = Snake(self.grid_width, self.grid_height, cell_size, 
                                 start_x=self.grid_width // 4, start_y=self.grid_height // 2)
        # AI: 오른쪽 시작
        self.ai_snake = Snake(self.grid_width, self.grid_height, cell_size, 
                             start_x=3 * self.grid_width // 4, start_y=self.grid_height // 2)
        self.ai_snake.direction = Direction.LEFT
        self.ai_snake.next_direction = Direction.LEFT
        
        self.food = Food(self.grid_width, self.grid_height, food_count=5)
        
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = None
        
        # 폰트 설정 (한글 지원 시스템 폰트 사용)
        try:
            # Windows에서 한글 지원 폰트
            self.font = pygame.font.SysFont("malgungothic", 32)
            self.game_over_font = pygame.font.SysFont("malgungothic", 64)
            self.small_font = pygame.font.SysFont("malgungothic", 20)
        except:
            # 폰트가 없으면 기본 폰트 사용
            self.font = pygame.font.Font(None, 36)
            self.game_over_font = pygame.font.Font(None, 72)
            self.small_font = pygame.font.Font(None, 24)
    
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player_snake.change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.player_snake.change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.player_snake.change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.player_snake.change_direction(Direction.RIGHT)
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
        
        return True
    
    def ai_move(self):
        """AI의 자동 움직임 (가장 가까운 음식을 향해 이동, 안전하게)"""
        head_x, head_y = self.ai_snake.get_head()
        
        # 가장 가까운 사과 찾기
        if not self.food.positions:
            return
        
        closest_food = min(self.food.positions, 
                          key=lambda f: abs(f[0] - head_x) + abs(f[1] - head_y))
        food_x, food_y = closest_food
        
        # 반대 방향 정의
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        # 다음 위치가 안전한지 확인하는 함수
        def is_safe(direction: Direction) -> bool:
            dx, dy = direction.value
            next_x = head_x + dx
            next_y = head_y + dy
            
            # 벽 충돌 확인
            if (next_x < 0 or next_x >= self.grid_width or
                next_y < 0 or next_y >= self.grid_height):
                return False
            
            # 자신의 몸과 충돌 확인 (머리 제외)
            if (next_x, next_y) in self.ai_snake.body[:-1]:
                return False
            
            return True
        
        # 모든 방향 중 안전한 방향 찾기
        safe_directions = []
        for direction in Direction:
            if direction != opposite.get(self.ai_snake.direction) and is_safe(direction):
                safe_directions.append(direction)
        
        # 안전한 방향이 없으면 현재 방향 유지
        if not safe_directions:
            return
        
        # 안전한 방향 중에서 사과에 가장 가까운 방향 선택
        best_direction = min(safe_directions,
                           key=lambda d: abs((head_x + d.value[0]) - food_x) + 
                                        abs((head_y + d.value[1]) - food_y))
        
        self.ai_snake.change_direction(best_direction)
    
    def check_snake_collision(self, snake1: Snake, snake2: Snake) -> bool:
        """두 뱀 사이의 충돌 확인"""
        # snake1의 머리가 snake2의 몸과 충돌
        if snake1.get_head() in snake2.body:
            return True
        return False
    
    def update(self):
        """게임 상태 업데이트"""
        if self.game_over:
            return
        
        # AI 움직임 결정
        self.ai_move()
        
        # 플레이어 뱀 이동
        if not self.player_snake.move():
            self.game_over = True
            self.winner = "AI"
            return
        
        # AI 뱀 이동
        if not self.ai_snake.move():
            self.game_over = True
            self.winner = "플레이어"
            return
        
        # 뱀 간 충돌 확인
        if self.check_snake_collision(self.player_snake, self.ai_snake):
            self.game_over = True
            self.winner = "AI"
            return
        
        if self.check_snake_collision(self.ai_snake, self.player_snake):
            self.game_over = True
            self.winner = "플레이어"
            return
        
        # 음식 먹기 처리
        occupied_cells = self.player_snake.body + self.ai_snake.body
        
        # 플레이어가 음식 먹음
        if self.player_snake.get_head() in self.food.positions:
            self.player_score += 10
            self.food.remove_food(self.player_snake.get_head())
            self.food.spawn_new(occupied_cells)
        else:
            self.player_snake.remove_tail()
        
        # AI가 음식 먹음
        if self.ai_snake.get_head() in self.food.positions:
            self.ai_score += 10
            self.food.remove_food(self.ai_snake.get_head())
            self.food.spawn_new(occupied_cells)
        else:
            self.ai_snake.remove_tail()
    
    def draw(self):
        """화면에 그리기"""
        # 배경 그리기
        self.screen.fill((0, 0, 0))
        
        # 격자 그리기
        self.draw_grid()
        
        # 뱀과 음식 그리기
        # 플레이어 뱀 (초록색)
        self.player_snake.draw(self.screen, self.cell_size, 
                              color_head=(0, 255, 0), color_body=(0, 200, 0))
        
        # AI 뱀 (파란색)
        self.ai_snake.draw(self.screen, self.cell_size, 
                          color_head=(0, 100, 255), color_body=(0, 50, 200))
        
        # 음식 그리기
        self.food.draw(self.screen, self.cell_size, color=(255, 200, 0))
        
        # 점수 표시
        player_score_text = self.font.render(f"플레이어: {self.player_score}", 
                                            True, (0, 255, 0))
        ai_score_text = self.font.render(f"AI: {self.ai_score}", 
                                        True, (0, 100, 255))
        
        self.screen.blit(player_score_text, (10, 10))
        self.screen.blit(ai_score_text, (self.width - 250, 10))
        
        # 게임 오버 화면
        if self.game_over:
            game_over_text = self.game_over_font.render("게임 끝", True, (255, 0, 0))
            winner_text = self.font.render(f"승자: {self.winner}", True, (255, 255, 0))
            restart_text = self.font.render("스페이스바 - 다시 시작", True, (255, 255, 255))
            
            text_rect = game_over_text.get_rect(
                center=(self.width // 2, self.height // 2 - 100))
            winner_rect = winner_text.get_rect(
                center=(self.width // 2, self.height // 2 - 20))
            restart_rect = restart_text.get_rect(
                center=(self.width // 2, self.height // 2 + 60))
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(winner_text, winner_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def draw_grid(self):
        """격자 그리기"""
        grid_color = (30, 30, 30)
        
        # 수평선
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y), 1)
        
        # 수직선
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height), 1)
    
    def reset_game(self):
        """게임 초기화"""
        self.player_snake = Snake(self.grid_width, self.grid_height, self.cell_size,
                                 start_x=self.grid_width // 4, start_y=self.grid_height // 2)
        self.ai_snake = Snake(self.grid_width, self.grid_height, self.cell_size,
                             start_x=3 * self.grid_width // 4, start_y=self.grid_height // 2)
        self.ai_snake.direction = Direction.LEFT
        self.ai_snake.next_direction = Direction.LEFT
        
        self.food = Food(self.grid_width, self.grid_height, food_count=5)
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = None
    
    def run(self):
        """게임 실행 루프"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()


def main():
    """게임 시작"""
    game = MultiSnakeGame(width=800, height=600, cell_size=20)
    game.run()


if __name__ == "__main__":
    main()
