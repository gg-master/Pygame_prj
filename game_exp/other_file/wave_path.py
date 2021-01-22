import pygame

WIDTH, HEIGHT = 300, 300
FPS = 30
CELL_SIZE = 30
EVENT_TYPE = 25


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = CELL_SIZE

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        k_s = 0
        for i in range(self.top,
                       self.cell_size * len(self.board) + self.top,
                       self.cell_size):
            k = 0
            for j in range(self.left,
                           self.cell_size * len(self.board[0]) + self.left,
                           self.cell_size):
                if self.board[k_s][k] == 0:
                    pygame.draw.rect(screen, pygame.Color('white'),
                                     (j, i,
                                      self.cell_size, self.cell_size), 1)
                elif self.board[k_s][k] == 1:
                    pygame.draw.rect(screen, pygame.Color('white'),
                                     (j, i,
                                      self.cell_size, self.cell_size), 1)
                    if self.player == 0:
                        pygame.draw.circle(screen, pygame.Color('red'),
                                           (j + self.cell_size // 2, i +
                                            self.cell_size // 2),
                                           (self.cell_size // 2) - 4, 2)
                        self.board[k_s][k] = 2
                    elif self.player == 1:
                        pygame.draw.line(screen, pygame.Color("blue"),
                                         (j + 2, i + 2),
                                         (j + self.cell_size - 2,
                                          i + self.cell_size - 2), 2)
                        pygame.draw.line(screen, pygame.Color("blue"),
                                         (j + self.cell_size - 2,
                                          i + 2),
                                         (j + 2,
                                          i + self.cell_size - 2), 2)
                        self.board[k_s][k] = 3

                elif self.board[k_s][k] == 2:
                    pygame.draw.rect(screen, pygame.Color('white'),
                                     (j, i,
                                      self.cell_size, self.cell_size), 1)
                    pygame.draw.circle(screen, pygame.Color('red'),
                                       (j + self.cell_size // 2, i +
                                        self.cell_size // 2),
                                       (self.cell_size // 2) - 4, 2)
                elif self.board[k_s][k] == 3:
                    pygame.draw.rect(screen, pygame.Color('white'),
                                     (j, i,
                                      self.cell_size, self.cell_size), 1)
                    pygame.draw.line(screen, pygame.Color("blue"),
                                     (j + 2, i + 2),
                                     (j + self.cell_size - 2,
                                      i + self.cell_size - 2), 2)
                    pygame.draw.line(screen, pygame.Color("blue"),
                                     (j + self.cell_size - 2,
                                      i + 2),
                                     (j + 2,
                                      i + self.cell_size - 2), 2)
                k += 1
            k_s += 1

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def on_click(self, cell_coords):
        # if cell_coords is not None:
        #     x, y = cell_coords
        #     self.board[y] = list(map(lambda z: int(not z), self.board[y]))
        #     for i in range(len(self.board)):
        #         for j in range(len(self.board[i])):
        #             if j == x and i != y:
        #                 self.board[i][j] = int(not self.board[i][j])
        if cell_coords is not None:
            x, y = cell_coords
            if self.board[y][x] == 0:
                self.board[y][x] = 1
                self.player = int(not self.player)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        if (x <= self.left or x >= self.left + len(
                self.board[0]) * self.cell_size) or \
            (y <= self.top or y >= self.top + len(
                self.board) * self.cell_size):
            return None
        c_x, c_y = 0, 0
        for i in range(self.left,
                       self.cell_size * len(self.board[0]) + self.left,
                       self.cell_size):
            if i <= x <= i + self.cell_size:
                break
            c_x += 1
        for i in range(self.top,
                       self.cell_size * len(self.board) + self.left,
                       self.cell_size):
            if i <= y <= i + self.cell_size:
                break
            c_y += 1
        return c_x, c_y


class Lines(Board):
    def __init__(self, size):
        super().__init__(size[0] // CELL_SIZE - 1,
                         size[1] // CELL_SIZE - 1)
        self.isMoving = False
        self.delay = 100
        self.poss = [[], []]

    def render(self):
        k_s = 0
        for i in range(self.top,
                       self.cell_size * len(self.board) + self.top,
                       self.cell_size):
            k = 0
            for j in range(self.left,
                           self.cell_size * len(self.board[0]) + self.left,
                           self.cell_size):
                if self.board[k_s][k] == 0:
                    pygame.draw.rect(screen, pygame.Color('white'),
                                     (j, i,
                                      self.cell_size, self.cell_size), 1)
                elif self.board[k_s][k] == 1:
                    pygame.draw.rect(screen, pygame.Color('white'),
                                     (j, i,
                                      self.cell_size, self.cell_size), 1)
                    pygame.draw.circle(screen, pygame.Color('blue'),
                                       (j + self.cell_size // 2, i +
                                        self.cell_size // 2),
                                       self.cell_size // 2 - 1)
                elif self.board[k_s][k] == 2:
                    pygame.draw.rect(screen, pygame.Color('white'),
                                     (j, i,
                                      self.cell_size, self.cell_size), 1)
                    pygame.draw.circle(screen, pygame.Color('red'),
                                       (j + self.cell_size // 2, i +
                                        self.cell_size // 2),
                                       self.cell_size // 2 - 1)
                k += 1
            k_s += 1

    def on_click(self, cell_coords):
        if cell_coords is not None and not self.isMoving:
            x, y = cell_coords
            if self.board[y][x] == 0:
                if self.is_there_red():
                    x_r, y_r = self.get_red_pos()
                    p = self.has_path(x_r, y_r, x, y)
                    if p[0]:
                        self.isMoving = True
                        self.poss = [[x_r, y_r], [x, y]]
                        pygame.time.set_timer(EVENT_TYPE, self.delay)
                else:
                    self.board[y][x] = 1
            elif self.board[y][x] == 1:
                self.board[y][x] = 2
            elif self.board[y][x] == 2:
                self.board[y][x] = 1

    def is_there_red(self):
        for i in self.board:
            if 2 in i:
                return True
        return False

    def has_path(self, x1, y1, x2, y2):
        INF = 1000
        x, y = x1, y1
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width \
                        and 0 <= next_y < self.height and \
                        self.is_free((next_x, next_y)) and \
                        distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = x2, y2
        if distance[y][x] == INF or (x1, y1) == (x2, y2):
            return False, (x1, y1)
        while prev[y][x] != (x1, y1):
            x, y = prev[y][x]
        return True, (x, y)

    def is_free(self, pos):
        if self.board[pos[1]][pos[0]] == 0:
            return True
        return False

    def get_red_pos(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 2:
                    return j, i

    def move_r(self):
        if self.isMoving:
            if self.poss[0] == self.poss[1]:
                self.isMoving = False
                pygame.time.set_timer(EVENT_TYPE, 0)
                return
            nex_pos = self.has_path(*self.poss[0], *self.poss[1])
            x, y = self.poss[0]
            self.board[y][x] = 0
            self.board[nex_pos[1][1]][nex_pos[1][0]] = 2
            self.poss = [[nex_pos[1][0], nex_pos[1][1]],
                         [self.poss[1][0], self.poss[1][1]]]


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    lines = Lines((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lines.get_click(event.pos)
            if event.type == EVENT_TYPE:
                lines.move_r()
        lines.render()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
