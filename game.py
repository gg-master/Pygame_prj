import pytmx
import pygame
from os import path
import os
import sys

MAPDIR = 'data\\maps\\'
WORLDIMG_DIR = 'world\\'
DIR_FOR_TANKS_IMG = 'tanks_texture\\'
WIDTH, HEIGHT = 950, 750
MAP_SIZE = 650
OFFSET = 50
FPS = 60

TILE_FOR_PLAYERS = 16
TILE_FOR_MOBS = 17

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
background = pygame.Surface((WIDTH, HEIGHT))

# Загрузка всей игровой графики
# img_dir = path.join(path.dirname(__file__),
#                     'E:/')
# powerup_images = dict()
# powerup_images['shield'] = \
#     pygame.image.load(path.join(img_dir,
#                                 'E:/Game on Python/SpaceShooterRedux'
#                                 '/PNG/Power-ups/shield_gold.png')).convert()
# powerup_images['gun'] = \
#     pygame.image.load(path.join(img_dir, 'E:/Game on Python/'
#                                          'SpaceShooterRedux/PNG/'
#                                          'Power-ups/bolt_gold.png')).convert()
#
# background = \
#     pygame.image.load(path.join(img_dir,
#                                 'Backgrounds/darkPurple.png')).convert()
# background = pygame.transform.scale(background, (WIDTH, HEIGHT))
# background_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))
#
# player_img = pygame.image.load(path.join(img_dir,
#                                          "PNG/playerShip1_red.png")).convert()
# player_mini_img = pygame.transform.scale(player_img, (35, 29))
# player_mini_img.set_colorkey(BLACK)
# # pictures for meteors
# meteor_list = []
# for m_i in ["PNG/Meteors/meteorBrown_med1.png",
#             "PNG/Meteors/meteorBrown_big1.png",
#             "PNG/Meteors/meteorGrey_med1.png"]:
#     meteor_list.append(pygame.image.load(path.join(img_dir, m_i)).convert())
#
# # pictures for bullet
# bullet_img = \
#     pygame.image.load(path.join(img_dir,
#                                 "PNG/Lasers/laserRed16.png")).convert()


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


class Player(pygame.sprite.Sprite):
    images = {
        '0_t0': 't_y.png', '0_l0': 't_y_l.png', '0_r0': 't_y_r.png',
        '0_b0': 't_y_b.png',
        '0_t1': 't_y1.png', '0_l1': 't_y1_l.png', '0_r1': 't_y1_r.png',
        '0_b1': 't_y1_b.png',
        '1_t0': 't_g.png', '1_l0': 't_g_l.png', '1_r0': 't_g_r.png',
        '1_b0': 't_g_b.png',
        '1_t1': 't_g1.png', '1_l1': 't_g1_l.png', '1_r1': 't_g1_r.png',
        '1_b1': 't_g1_b.png',
    }

    def __init__(self, x, y, layer, tile_size, player):
        super().__init__()
        self.type_tanks = 't1'
        self.player = player
        self.side = 't'
        self.move_trigger = False

        self.TILE_SIZE = tile_size
        self.image = None
        self.mask = None
        self.load_tanks_image()

        self.coords = [x, y]
        self.rect = self.image.get_rect()
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

        self.layer = layer
        self.speed = 2
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.bullet = None

        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()

    def load_tanks_image(self):
        self.move_trigger = not self.move_trigger
        image = load_image(f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{self.images[f"{self.player}_{self.side}{int(self.move_trigger)}"]}'
                           if self.player == 0 else
                           f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{self.images[f"{self.player}_{self.side}{int(self.move_trigger)}"]}')
        self.image = pygame.transform.scale(image, (self.TILE_SIZE -
                                                    self.TILE_SIZE // 8,
                                                    self.TILE_SIZE -
                                                    self.TILE_SIZE // 8))
        s = pygame.Surface((self.image.get_rect().width,
                            self.image.get_rect().height), pygame.SRCALPHA)
        s.fill(pygame.color.Color('black'))
        self.mask = pygame.mask.from_surface(s)

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def move(self, keystate, walls):
        if keystate[pygame.K_UP]:
            self.side = 't'
            self.load_tanks_image()
            self.rect = self.rect.move(0, -self.speed)
            c = pygame.sprite.spritecollide(self, walls, False,
                                            pygame.sprite.collide_mask)
            if c:
                self.rect = self.rect.move(0, self.speed)
        elif keystate[pygame.K_DOWN]:
            self.side = 'b'
            self.load_tanks_image()
            self.rect = self.rect.move(0, self.speed)
            c = pygame.sprite.spritecollide(self, walls, False,
                                            pygame.sprite.collide_mask)
            if c:
                self.rect = self.rect.move(0, -self.speed)
        elif keystate[pygame.K_LEFT]:
            self.side = 'l'
            self.load_tanks_image()
            self.rect = self.rect.move(-self.speed, 0)
            c = pygame.sprite.spritecollide(self, walls, False,
                                            pygame.sprite.collide_mask)
            if c:
                self.rect = self.rect.move(self.speed, 0)

        elif keystate[pygame.K_RIGHT]:
            self.side = 'r'
            self.load_tanks_image()
            self.rect = self.rect.move(self.speed, 0)
            c = pygame.sprite.spritecollide(self, walls, False,
                                            pygame.sprite.collide_mask)
            if c:
                self.rect = self.rect.move(-self.speed, 0)

    def update(self, walls):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        keystate = pygame.key.get_pressed()
        self.move(keystate, walls)

        if keystate[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.bullet is None or not self.bullet.alive():
                bullet = Bullet(self.rect, self.side)
                bullet.add(game.all_sprites, game.bullets)
                self.bullet = bullet


class Bullet(pygame.sprite.Sprite):
    images = {
        't': 'b.png',
        'l': 'b_l.png',
        'r': 'b_r.png',
        'b': 'b_b.png'
    }

    def __init__(self, rect_tank, side: str):
        super().__init__()
        self.image = load_image(f'{DIR_FOR_TANKS_IMG}'
                                f'bullet\\{self.images[side]}')
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.side = side
        self.speed = 5
        self.speedy, self.speedx = 0, 0
        self.set_rect(rect_tank)

    def update(self):
        self.rect = self.rect.move(self.speedx, self.speedy)
        # удалить спрайт, если он заходит за верхнюю часть экрана
        if self.rect.y < game.map.rect.y \
                or self.rect.x < game.map.rect.x \
                or self.rect.x > game.map.rect.right \
                or self.rect.y > game.map.rect.bottom:
            self.kill()
        # TODO столкновне с другими пулями, игроками, стенами.
        c = pygame.sprite.spritecollideany(self, game.all_sprites)
        if c is not None:
            if c in game.wall_group and c.isWall:
                coord_collide = pygame.sprite.collide_mask(c, self)
                if coord_collide is not None:
                    c.change_yourself(coord_collide)
                    self.kill()

    def set_rect(self, rect_tank):
        if self.side == 't':
            self.rect.bottom = rect_tank.top
            self.rect.centerx = rect_tank.centerx
            self.speedy = -self.speed
        if self.side == 'l':
            self.rect.right = rect_tank.left
            self.rect.centery = rect_tank.centery
            self.speedx = -self.speed
        if self.side == 'r':
            self.rect.left = rect_tank.right
            self.rect.centery = rect_tank.centery
            self.speedx = self.speed
        if self.side == 'b':
            self.rect.top = rect_tank.bottom
            self.rect.centerx = rect_tank.centerx
            self.speedy = self.speed


def convert_coords(x, tile_size):
    return x[0] * tile_size + OFFSET, x[1] * tile_size + OFFSET, x[2]


class Map:
    def __init__(self, path, map_size):
        self.map = pytmx.load_pygame(path)
        self.TILE_SIZE = map_size // self.map.width
        self.width = self.map.width
        self.height = self.map.height
        self.koeff = self.map.tilewidth / self.TILE_SIZE
        self.rect = pygame.rect.Rect((OFFSET, OFFSET),
                                     (MAP_SIZE, MAP_SIZE))

    def get_tile_image(self, x, y, layer):
        image = self.map.get_tile_image(x, y, layer)
        if image is not None:
            image = pygame.transform.scale(image,
                                           (self.TILE_SIZE, self.TILE_SIZE))
            return image

    def get_objects(self, name):
        return self.map.layernames[name]

    def get_tile_id(self, gid):
        return self.map.tiledgidmap[gid]

    def get_tiled_by_id(self, id):
        return list(map(lambda x: convert_coords(x, self.TILE_SIZE),
                        self.map.get_tile_locations_by_gid(
            list(self.map.tiledgidmap.values()).index(id) + 1)))

    def render_layer(self, screen, layer):
        for x in range(self.width):
            for y in range(self.height):
                image = self.get_tile_image(x, y, layer)
                if image is not None:
                    screen.blit(image, (
                        x * self.TILE_SIZE + OFFSET,
                        y * self.TILE_SIZE + OFFSET))


class Wall(pygame.sprite.Sprite):
    type_wall = {
        3: 'wall_RT.png',
        4: 'wall_RD.png',
        5: 'wall_LT.png',
        6: 'wall_LD.png',
        7: 'wall_T.png',
        8: 'wall_R.png',
        9: 'wall_L.png',
        10: 'wall_D.png',
        11: 'wall_1.png',
        18: 'wall_b1.png',
        19: 'wall_b2.png',
        20: 'wall_b3.png',
        21: 'wall_b4.png',
        22: 'wall_h1.png',
        23: 'wall_h2.png',
        2: 'water.png',
        13: 'metall_wall.png'
    }  # key(id) from Tiled Edit

    def __init__(self, x, y, id, tile_size):
        super().__init__()
        self.isBroken = True if id not in [2, 13] else False
        self.isWall = True if id not in [2] else False

        self.tile_size = tile_size
        self.id = id
        self.image = self.mask = None
        self.reload_mask()
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def reload_mask(self):
        self.image = load_image(f'{WORLDIMG_DIR}{self.type_wall[self.id]}')
        self.image = pygame.transform.scale(self.image,
                                            (self.tile_size, self.tile_size))
        self.mask = pygame.mask.from_surface(self.image)

    def change_yourself(self, coords):
        x, y = coords
        if self.id == 11:
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.id = 5
                self.reload_mask()
            elif 50 >= x >= 25 >= y >= 0:
                self.id = 3
                self.reload_mask()
            elif 0 <= x <= 25 <= y <= 50:
                self.id = 6
                self.reload_mask()
            elif 50 >= x >= 25 and 25 <= y <= 50:
                self.id = 4
                self.reload_mask()
        elif self.id == 5:
            if x >= 25 >= y >= 0:
                self.id = 7
                self.reload_mask()
            elif 25 <= x <= 50 and 25 <= y <= 50:
                self.id = 22
                self.reload_mask()
            elif 0 <= x <= 25 <= y <= 50:
                self.id = 9
                self.reload_mask()
        elif self.id == 3:
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.id = 7
                self.reload_mask()
            elif 0 <= x <= 25 <= y <= 50:
                self.id = 23
                self.reload_mask()
            elif 25 <= x <= 50 and 25 <= y <= 50:
                self.id = 8
                self.reload_mask()
        elif self.id == 6:
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.id = 9
                self.reload_mask()
            elif 50 >= x >= 25 >= y >= 0:
                self.id = 23
                self.reload_mask()
            elif 25 <= x <= 50 and 25 <= y <= 50:
                self.id = 10
                self.reload_mask()
        elif self.id == 4:
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.id = 22
                self.reload_mask()
            elif 50 >= x >= 25 >= y >= 0:
                self.id = 8
                self.reload_mask()
            elif 0 <= x <= 25 <= y <= 50:
                self.id = 10
                self.reload_mask()
        elif self.id == 10:
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.id = 19
                self.reload_mask()
            if 50 >= x >= 25 >= y >= 0:
                self.id = 21
                self.reload_mask()
        elif self.id == 7:
            if 0 <= x <= 25 <= y <= 50:
                self.id = 20
                self.reload_mask()
            if 50 >= x >= 25 and 25 <= y <= 50:
                self.id = 18
                self.reload_mask()
        elif self.id == 9:
            if 50 >= x >= 25 >= y >= 0:
                self.id = 20
                self.reload_mask()
            if 50 >= x >= 25 and 25 <= y <= 50:
                self.id = 19
                self.reload_mask()
        elif self.id == 8:
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.id = 18
                self.reload_mask()
            if 0 <= x <= 25 <= y <= 50:
                self.id = 21
                self.reload_mask()
        elif self.id == 22:
            if 50 >= x >= 25 >= y >= 0:
                self.id = 18
                self.reload_mask()
            if 0 <= x <= 25 <= y <= 50:
                self.id = 19
                self.reload_mask()
        elif self.id == 23:
            if 50 >= x >= 25 and 25 <= y <= 50:
                self.id = 21
                self.reload_mask()
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.id = 20
                self.reload_mask()
        else:
            self.kill()


class Game:
    def __init__(self, type_game, number_level):
        self.map = Map(f'{MAPDIR}map{number_level}.tmx', MAP_SIZE)
        self.map_object = self.map.map
        self.TILE_SIZE = self.map.TILE_SIZE

        self.all_sprites = pygame.sprite.Group()
        self.mobs_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        # Создаем спрайты стен
        self.createWalls()

        # для игроков ДОЛЖНО быть минимум и максимум 2
        # доступные клетки для спавна (В ДАННЫЙ МОМЕНТ УЧИТЫВАЕТСЯ
        # РЕЖИМ ЛИШЬ ТОЛЬКО НА 2 ЧЕЛОВЕК МАКСИМУМ)
        self.TILES_FOR_PLAYERS = self.map.get_tiled_by_id(TILE_FOR_PLAYERS)
        self.TILES_FOR_MOBS = self.map.get_tiled_by_id(TILE_FOR_MOBS)
        # print(self.TILES_FOR_PLAYERS)
        self.player1 = None
        self.player2 = None
        if type_game == 1:
            self.player1 = Player(*self.TILES_FOR_PLAYERS[0],
                                  self.TILE_SIZE, player=0)
            if type_game == 2:
                self.player2 = Player(*self.TILES_FOR_PLAYERS[1],
                                      self.TILE_SIZE, player=1)
        elif type_game == 3:
            raise Exception('Онлайн еще не готов')
        else:
            raise Exception('Неверный тип игры')
        if self.player1 is not None:
            self.player1.add(self.player_group, self.all_sprites)
        if self.player2 is not None:
            self.player2.add(self.player_group, self.all_sprites)

    def createWalls(self):
        for i in self.map.get_objects('walls'):
            x, y = i.x / self.map.koeff + OFFSET, i.y / self.map.koeff + OFFSET
            wall = Wall(x, y, self.map.get_tile_id(i.gid), self.TILE_SIZE)
            wall.add(self.all_sprites, self.wall_group)

    def update(self, events=None):
        self.player_group.update(self.wall_group)
        self.bullets.update()

    def render(self):
        # Отрисовка по слоям.
        """
        Карта должна содержать минимум 4 слоя тайлов.
        0. Земля
        1. места для спавна игрков
        2. места для спавна ботов
        3. Деревья
        """
        # Отрисовка первого слоя (основного)
        self.map.render_layer(screen, 0)
        # render player and bullet and mobs

        self.wall_group.draw(screen)
        self.all_sprites.draw(screen)
        # Отрисовка второго слоя (деревья и тп)
        self.map.render_layer(screen, 3)


fullscreen = False


if __name__ == '__main__':
    clock = pygame.time.Clock()
    running = True
    game = Game(1, 1)
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h),
                                                     pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(monitor_size,
                                                         pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(
                            (screen.get_width(), screen.get_height()),
                            pygame.RESIZABLE)
            game.update(event)
        game.update()
        game.render()

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
