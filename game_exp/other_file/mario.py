import pygame
import sys
import os

WIDTH, HEIGHT = 500, 500
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    # for line in intro_text:
    #     string_rendered = font.render(line, 1, pygame.Color('black'))
    #     intro_rect = string_rendered.get_rect()
    #     text_coord += 10
    #     intro_rect.top = text_coord
    #     intro_rect.x = 10
    #     text_coord += intro_rect.height
    #     screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))
    except Exception:
        print('Файл уровня не найден')
        exit()


tile_width = tile_height = 50

tile_images = {
    'wall': pygame.transform.scale(load_image('tree.png'), (tile_width, tile_height)),
    'empty': pygame.transform.scale(load_image('ground.png'), (tile_width, tile_height))
}
player_image = pygame.transform.scale(load_image('green_tank.png'), (tile_width, tile_height))


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.isWall = False if tile_type == 'empty' else True
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self, *args):
        # print(self.rect)
        if self.rect.left >= WIDTH:
            r = self.rect.left - WIDTH
            self.rect.left = r - WIDTH
        elif self.rect.right <= 0:
            r = self.rect.right + WIDTH
            self.rect.right = r + WIDTH
        elif self.rect.top > HEIGHT:
            r = self.rect.top - HEIGHT / 2.5
            self.rect.top = r - HEIGHT
        elif self.rect.bottom < 0:
            r = self.rect.bottom + HEIGHT / 2.5
            self.rect.bottom = r + HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.angle = 0

    def update(self, *args):
        if args:
            if args[0].type == pygame.KEYDOWN:
                if args[0].key == pygame.K_DOWN:
                    self.rect = self.rect.move(0, tile_width)
                    c = pygame.sprite.spritecollideany(self, tiles_group)
                    self.image = pygame.transform.rotate(self.image,
                                                         self.angle)
                    self.angle = 180
                    if c is not None and c.isWall:
                        self.rect = self.rect.move(0, -tile_width)

                elif args[0].key == pygame.K_UP:
                    self.rect = self.rect.move(0, -tile_width)
                    c = pygame.sprite.spritecollideany(self, tiles_group)
                    self.image = pygame.transform.rotate(self.image,
                                                         abs(self.angle))
                    self.angle = 0
                    if c is not None and c.isWall:
                        self.rect = self.rect.move(0, tile_width)
                elif args[0].key == pygame.K_LEFT:
                    self.rect = self.rect.move(-tile_width, 0)
                    c = pygame.sprite.spritecollideany(self, tiles_group)
                    self.image = pygame.transform.rotate(self.image, -90)
                    self.angle = -90
                    if c is not None and c.isWall:
                        self.rect = self.rect.move(tile_width, 0)

                elif args[0].key == pygame.K_RIGHT:
                    self.rect = self.rect.move(tile_width, 0)
                    c = pygame.sprite.spritecollideany(self, tiles_group)
                    self.image = pygame.transform.rotate(self.image, 0)
                    self.angle = 90
                    if c is not None and c.isWall:
                        self.rect = self.rect.move(-tile_width, 0)


def choose_level():
    try:
        c = input('Введите название карты уровня: ')
        return c
    except Exception:
        print('Неправильно введено название')


if __name__ == '__main__':
    clock = pygame.time.Clock()
    camera = Camera()
    running = True
    l_l = load_level(choose_level())

    start_screen()
    player, level_x, level_y = generate_level(l_l)

    while running:
        screen.fill(pygame.Color('white'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            player.update(event)

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        all_sprites.draw(screen)
        all_sprites.update()
        player_group.draw(screen)

        # pygame.draw.polygon(screen, pygame.color.Color('black'),
        #                     ((0, 0), (WIDTH, 0), (WIDTH, 30), (0, 30)))
        # pygame.draw.polygon(screen, pygame.color.Color('black'),
        #                     ((WIDTH, 0), (WIDTH, HEIGHT), (WIDTH - 30, HEIGHT),
        #                      (WIDTH - 30, 0)))
        # pygame.draw.polygon(screen, pygame.color.Color('black'),
        #                     ((0, 0), (30, 0), (30, HEIGHT), (0, HEIGHT)))
        # pygame.draw.polygon(screen, pygame.color.Color('black'),
        #                     ((0, HEIGHT - 30), (0, HEIGHT), (WIDTH, HEIGHT),
        #                      (WIDTH, HEIGHT - 30)))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
