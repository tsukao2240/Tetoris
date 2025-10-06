import pygame
import random
import sys

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# ゲーム設定
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
BOARD_X = 50
BOARD_Y = 50

# テトロミノの形状定義
TETROMINOES = {
    'I': {
        'shape': [
            ['.....',
             '..#..',
             '..#..',
             '..#..',
             '..#..'],
            ['.....',
             '.....',
             '####.',
             '.....',
             '.....']
        ],
        'color': CYAN
    },
    'O': {
        'shape': [
            ['.....',
             '.....',
             '.##..',
             '.##..',
             '.....']
        ],
        'color': YELLOW
    },
    'T': {
        'shape': [
            ['.....',
             '.....',
             '.#...',
             '###..',
             '.....'],
            ['.....',
             '.....',
             '.#...',
             '.##..',
             '.#...'],
            ['.....',
             '.....',
             '.....',
             '###..',
             '.#...'],
            ['.....',
             '.....',
             '.#...',
             '##...',
             '.#...']
        ],
        'color': PURPLE
    },
    'S': {
        'shape': [
            ['.....',
             '.....',
             '.##..',
             '##...',
             '.....'],
            ['.....',
             '.#...',
             '.##..',
             '..#..',
             '.....']
        ],
        'color': GREEN
    },
    'Z': {
        'shape': [
            ['.....',
             '.....',
             '##...',
             '.##..',
             '.....'],
            ['.....',
             '..#..',
             '.##..',
             '.#...',
             '.....']
        ],
        'color': RED
    },
    'J': {
        'shape': [
            ['.....',
             '.#...',
             '.#...',
             '##...',
             '.....'],
            ['.....',
             '.....',
             '#....',
             '###..',
             '.....'],
            ['.....',
             '.##..',
             '.#...',
             '.#...',
             '.....'],
            ['.....',
             '.....',
             '###..',
             '..#..',
             '.....']
        ],
        'color': BLUE
    },
    'L': {
        'shape': [
            ['.....',
             '..#..',
             '..#..',
             '.##..',
             '.....'],
            ['.....',
             '.....',
             '###..',
             '#....',
             '.....'],
            ['.....',
             '##...',
             '.#...',
             '.#...',
             '.....'],
            ['.....',
             '.....',
             '..#..',
             '###..',
             '.....']
        ],
        'color': ORANGE
    }
}

class Tetromino:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.shape = TETROMINOES[shape_type]['shape']
        self.color = TETROMINOES[shape_type]['color']
        self.x = BOARD_WIDTH // 2 - 2
        self.y = 0
        self.rotation = 0

    def get_rotated_shape(self, rotation=None):
        if rotation is None:
            rotation = self.rotation
        return self.shape[rotation % len(self.shape)]

    def get_cells(self, x=None, y=None, rotation=None):
        # 現在の位置でのセルの座標を取得
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        shape = self.get_rotated_shape(rotation)
        cells = []

        for row_index, row in enumerate(shape):
            for col_index, cell in enumerate(row):
                if cell == '#':
                    cells.append((x + col_index, y + row_index))

        return cells

class TetrisGame:
    def __init__(self):
        self.board = [[BLACK for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # ミリ秒
        self.game_over = False

        self.spawn_piece()

    def spawn_piece(self):
        if self.next_piece is None:
            self.current_piece = Tetromino(random.choice(list(TETROMINOES.keys())))
            self.next_piece = Tetromino(random.choice(list(TETROMINOES.keys())))
        else:
            self.current_piece = self.next_piece
            self.next_piece = Tetromino(random.choice(list(TETROMINOES.keys())))

        # ゲームオーバー判定
        if not self.is_valid_position(self.current_piece):
            self.game_over = True

    def is_valid_position(self, piece, x=None, y=None, rotation=None):
        cells = piece.get_cells(x, y, rotation)

        for cell_x, cell_y in cells:
            # 境界チェック
            if cell_x < 0 or cell_x >= BOARD_WIDTH or cell_y >= BOARD_HEIGHT:
                return False

            # ボードの既存ピースとの衝突チェック
            if cell_y >= 0 and self.board[cell_y][cell_x] != BLACK:
                return False

        return True

    def move_piece(self, dx, dy):
        if self.current_piece and self.is_valid_position(self.current_piece,
                                                         self.current_piece.x + dx,
                                                         self.current_piece.y + dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        if self.current_piece:
            new_rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
            if self.is_valid_position(self.current_piece, rotation=new_rotation):
                self.current_piece.rotation = new_rotation
                return True
        return False

    def drop_piece(self):
        # ピースを可能な限り下に移動
        while self.move_piece(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        # 現在のピースをボードに固定
        cells = self.current_piece.get_cells()
        for cell_x, cell_y in cells:
            if cell_y >= 0:
                self.board[cell_y][cell_x] = self.current_piece.color

        # ライン消去チェック
        self.clear_lines()

        # 新しいピースを生成
        self.spawn_piece()

    def clear_lines(self):
        lines_to_clear = []

        # 完成したラインを検索
        for y in range(BOARD_HEIGHT):
            if all(cell != BLACK for cell in self.board[y]):
                lines_to_clear.append(y)

        # ラインを削除
        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [BLACK for _ in range(BOARD_WIDTH)])

        # スコア計算
        if lines_to_clear:
            lines_cleared = len(lines_to_clear)
            self.lines_cleared += lines_cleared

            # スコア計算（テトリスの標準的なスコアリング）
            line_scores = {1: 40, 2: 100, 3: 300, 4: 1200}
            self.score += line_scores.get(lines_cleared, 0) * (self.level + 1)

            # レベルアップ判定
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)

    def update(self, dt):
        if self.game_over:
            return

        self.fall_time += dt

        # 自動落下
        if self.fall_time >= self.fall_speed:
            if not self.move_piece(0, 1):
                self.lock_piece()
            self.fall_time = 0

class TetrisRenderer:
    def __init__(self, screen):
        self.screen = screen
        # 日本語対応のシステムフォントを使用
        try:
            # Windowsの場合
            self.font = pygame.font.SysFont('msgothic', 36)
            self.small_font = pygame.font.SysFont('msgothic', 20)
        except:
            try:
                # その他のシステムの場合
                self.font = pygame.font.SysFont('arial', 36)
                self.small_font = pygame.font.SysFont('arial', 20)
            except:
                # フォールバック
                self.font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 20)

    def draw_board(self, game):
        # ボードの背景を描画
        board_rect = pygame.Rect(BOARD_X, BOARD_Y,
                                BOARD_WIDTH * CELL_SIZE,
                                BOARD_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, WHITE, board_rect)
        pygame.draw.rect(self.screen, GRAY, board_rect, 2)

        # ボードのセルを描画
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                cell_rect = pygame.Rect(BOARD_X + x * CELL_SIZE,
                                      BOARD_Y + y * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE)
                color = game.board[y][x]
                if color != BLACK:
                    pygame.draw.rect(self.screen, color, cell_rect)
                    pygame.draw.rect(self.screen, BLACK, cell_rect, 1)

        # 現在のピースを描画
        if game.current_piece:
            cells = game.current_piece.get_cells()
            for cell_x, cell_y in cells:
                if 0 <= cell_x < BOARD_WIDTH and cell_y >= 0:
                    cell_rect = pygame.Rect(BOARD_X + cell_x * CELL_SIZE,
                                          BOARD_Y + cell_y * CELL_SIZE,
                                          CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, game.current_piece.color, cell_rect)
                    pygame.draw.rect(self.screen, BLACK, cell_rect, 1)

        # グリッドを描画
        for x in range(BOARD_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY,
                           (BOARD_X + x * CELL_SIZE, BOARD_Y),
                           (BOARD_X + x * CELL_SIZE, BOARD_Y + BOARD_HEIGHT * CELL_SIZE))
        for y in range(BOARD_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                           (BOARD_X, BOARD_Y + y * CELL_SIZE),
                           (BOARD_X + BOARD_WIDTH * CELL_SIZE, BOARD_Y + y * CELL_SIZE))

    def draw_next_piece(self, game):
        if not game.next_piece:
            return

        next_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 20
        next_y = BOARD_Y + 20

        # 「次のピース」ラベル
        try:
            text = self.small_font.render("次のピース", True, WHITE)
        except:
            text = self.small_font.render("NEXT", True, WHITE)
        self.screen.blit(text, (next_x, next_y - 30))

        # 次のピースを描画
        shape = game.next_piece.get_rotated_shape(0)
        for row_index, row in enumerate(shape):
            for col_index, cell in enumerate(row):
                if cell == '#':
                    cell_rect = pygame.Rect(next_x + col_index * 20,
                                          next_y + row_index * 20,
                                          20, 20)
                    pygame.draw.rect(self.screen, game.next_piece.color, cell_rect)
                    pygame.draw.rect(self.screen, BLACK, cell_rect, 1)

    def draw_stats(self, game):
        stats_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 20
        stats_y = BOARD_Y + 150

        # スコア表示
        try:
            score_text = self.small_font.render(f"スコア: {game.score}", True, WHITE)
        except:
            score_text = self.small_font.render(f"SCORE: {game.score}", True, WHITE)
        self.screen.blit(score_text, (stats_x, stats_y))

        # レベル表示
        try:
            level_text = self.small_font.render(f"レベル: {game.level}", True, WHITE)
        except:
            level_text = self.small_font.render(f"LEVEL: {game.level}", True, WHITE)
        self.screen.blit(level_text, (stats_x, stats_y + 30))

        # 消去ライン数表示
        try:
            lines_text = self.small_font.render(f"ライン: {game.lines_cleared}", True, WHITE)
        except:
            lines_text = self.small_font.render(f"LINES: {game.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (stats_x, stats_y + 60))

    def draw_game_over(self, game):
        if game.game_over:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            try:
                game_over_text = self.font.render("ゲームオーバー", True, WHITE)
            except:
                game_over_text = self.font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2,
                                                       self.screen.get_height() // 2 - 50))
            self.screen.blit(game_over_text, text_rect)

            try:
                restart_text = self.small_font.render("Rキーでリスタート", True, WHITE)
            except:
                restart_text = self.small_font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2,
                                                        self.screen.get_height() // 2))
            self.screen.blit(restart_text, restart_rect)

            try:
                score_text = self.small_font.render(f"最終スコア: {game.score}", True, WHITE)
            except:
                score_text = self.small_font.render(f"FINAL SCORE: {game.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(self.screen.get_width() // 2,
                                                    self.screen.get_height() // 2 + 30))
            self.screen.blit(score_text, score_rect)

    def draw_controls(self):
        controls_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 20
        controls_y = BOARD_Y + 300

        try:
            controls = [
                "操作方法:",
                "←→: 移動",
                "↓: 高速落下",
                "↑: 回転",
                "スペース: 即座に落下",
                "R: リスタート",
                "ESC: 終了"
            ]
        except:
            controls = [
                "CONTROLS:",
                "LEFT/RIGHT: Move",
                "DOWN: Fast Drop",
                "UP: Rotate",
                "SPACE: Hard Drop",
                "R: Restart",
                "ESC: Quit"
            ]

        for i, control in enumerate(controls):
            color = WHITE if i == 0 else GRAY
            font = self.small_font if i == 0 else self.small_font
            try:
                text = font.render(control, True, color)
            except:
                # 英語版のフォールバック
                english_controls = [
                    "CONTROLS:",
                    "LEFT/RIGHT: Move",
                    "DOWN: Fast Drop",
                    "UP: Rotate",
                    "SPACE: Hard Drop",
                    "R: Restart",
                    "ESC: Quit"
                ]
                text = font.render(english_controls[i], True, color)
            self.screen.blit(text, (controls_x, controls_y + i * 20))

def main():
    pygame.init()

    # 画面サイズの設定
    screen_width = BOARD_X + BOARD_WIDTH * CELL_SIZE + 200
    screen_height = BOARD_Y + BOARD_HEIGHT * CELL_SIZE + 100
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("テトリス")

    clock = pygame.time.Clock()
    game = TetrisGame()
    renderer = TetrisRenderer(screen)

    # キーリピート設定
    key_repeat_delay = 200  # ミリ秒
    key_repeat_interval = 50  # ミリ秒
    last_key_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_DOWN: 0}

    running = True
    while running:
        dt = clock.tick(60)  # 60 FPS
        current_time = pygame.time.get_ticks()

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game = TetrisGame()  # ゲームリスタート
                elif not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move_piece(-1, 0)
                        last_key_time[pygame.K_LEFT] = current_time
                    elif event.key == pygame.K_RIGHT:
                        game.move_piece(1, 0)
                        last_key_time[pygame.K_RIGHT] = current_time
                    elif event.key == pygame.K_DOWN:
                        game.move_piece(0, 1)
                        last_key_time[pygame.K_DOWN] = current_time
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.drop_piece()

        # キー連続入力処理
        if not game.game_over:
            keys = pygame.key.get_pressed()

            # 左右移動のキーリピート
            if keys[pygame.K_LEFT] and current_time - last_key_time[pygame.K_LEFT] > key_repeat_delay:
                if current_time - last_key_time[pygame.K_LEFT] > key_repeat_interval:
                    game.move_piece(-1, 0)
                    last_key_time[pygame.K_LEFT] = current_time - key_repeat_delay + key_repeat_interval

            if keys[pygame.K_RIGHT] and current_time - last_key_time[pygame.K_RIGHT] > key_repeat_delay:
                if current_time - last_key_time[pygame.K_RIGHT] > key_repeat_interval:
                    game.move_piece(1, 0)
                    last_key_time[pygame.K_RIGHT] = current_time - key_repeat_delay + key_repeat_interval

            # 下移動のキーリピート（より高速）
            if keys[pygame.K_DOWN] and current_time - last_key_time[pygame.K_DOWN] > 50:
                game.move_piece(0, 1)
                last_key_time[pygame.K_DOWN] = current_time

        # ゲームの更新
        game.update(dt)

        # 画面描画
        screen.fill(BLACK)
        renderer.draw_board(game)
        renderer.draw_next_piece(game)
        renderer.draw_stats(game)
        renderer.draw_controls()
        renderer.draw_game_over(game)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()