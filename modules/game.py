import pytmx
import pygame
import os
from modules.sprites import Player, Bot, Eagle, Wall, EmptyBot

"""
Карта должна содержать минимум эти слои.
0. ground - layer tiles
1. spawn_players - layer tiles
2. spawn_bots - layer tiles
3. eagle - object

Также могут быть использованы:
walls - objects
trees - layer - tiles
"""

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
monitor_size = [pygame.display.Info().current_w,
                pygame.display.Info().current_h]
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


def convert_coords(x, tile_size):
    """Изменяем координаты в соответсвии со смещением"""
    return x[0] * tile_size + OFFSET, x[1] * tile_size + OFFSET, x[2]


class BotManager:
    def __init__(self, game_obj):
        self.game = game_obj
        # В зависимости от количества игроков на поле должно
        # быть или 4 или 6 вражеских танков
        self.player_count = 1 if self.game.player1 is not None \
            else 2 if self.game.player2 is not None else 0
        if self.player_count == 0:
            raise Exception('Недостаточно игроков')
        from modules import mobs_count
        """Загружаем шаблон, по которому будут спавниться боты"""
        # TODO когда необходимого шаблона нет, то
        #  необходимо или зациклить или написать генератор шаблона
        try:
            self.bot_comb = mobs_count.count[self.game.level]
            # self.bot_comb = mobs_count.count[10]
        except KeyError:
            raise KeyError('Комбинация ботов не найдена')

        # Определяем время респавна ботов
        # (динамическое и зависит от уровня и количества игроков)
        self.respawn_time = (190 - self.game.level * 4 - (
                self.player_count - 1) * 60) * 10
        self.start_time = -self.respawn_time
        """В игре существует 3 временных периода когда:
        1: боты просто катаются по карте и ничего не преследуют
        2: боты едут к ближайшему игроку
        3: боты едут к орлу
        """
        self.period_timer = pygame.time.get_ticks()
        self.first_period = self.respawn_time // 8 * 20
        self.second_period = self.first_period * 2
        self.third_period = 2560 + self.second_period

        self.global_count_bots = sum(self.bot_comb)
        self.types_tanks = ['t1', 't2', 't3', 't4']
        self.real_time_counter = [0, self.get_type()]
        self.visible_bots = 4 if self.player_count == 1 else 6
        self.free_tiles_for_spawn = self.game.TILES_FOR_MOBS

        self.bonus_timer = None
        self.bonus_delay = None
        self.bonus_name = None

    def update(self, events=None):
        now = pygame.time.get_ticks()
        self.check_bonuses()
        # Определяем убиты ли все боты. Если убиты, то игрок выйграл
        if len(self.game.mobs_group) <= 0 and self.global_count_bots <= 0:
            self.game.isGameOver = True
            self.game.game_over()
        # Если игра продолжается, то мы создаем бота в
        # зависимости от времени респавна и количества ботов на карте
        if not self.game.isGameOver and \
                now - self.start_time > self.respawn_time and \
                len(self.game.mobs_group) < 4 and self.global_count_bots > 0:
            tile = self.get_tile()
            if tile:
                Bot(self.game, tile,
                    self.game.TILE_SIZE, self.get_type_tank(),
                    sum(self.bot_comb) - self.global_count_bots)
                self.start_time = now

        # Проверяем на периоды и устанавливаем цели.
        # Через сравнения достагается цикличность периодов
        if self.first_period < now - self.period_timer < self.second_period:
            self.set_target_for_bots('players')
        elif self.second_period < now - self.period_timer \
                < self.third_period:
            self.set_target_for_bots('eagle')  # eagle
        elif now - self.period_timer > self.third_period:
            self.set_target_for_bots(None)  # None
            # Этот таймер как раз таки и помогает реализовать цикличность
            self.period_timer = now

        self.game.mobs_group.update(events)

    def get_type(self):
        for i in range(len(self.bot_comb)):
            if self.bot_comb[i]:
                return self.types_tanks[i]

    def get_type_tank(self):
        """Функция, отвечающая за подсчет и контроль
        количества и типов танков
        :return type_bot like t1 or t2 or t3 or t4"""
        # Уменьшаем счетчик общего количества ботов
        self.global_count_bots -= 1
        # Увеличиваем счетчик количества ботов определенного типа
        self.real_time_counter[0] += 1
        # Когда количество ботов больше чем в шаблоне для данного
        # уровня данного типа танка, мы изменяем тип и сбрасываем счетчик
        if self.real_time_counter[0] \
                > self.bot_comb[self.types_tanks.index(self.real_time_counter[
                                                           1])]:
            self.real_time_counter[0] = 1
            self.real_time_counter[1] = self.types_tanks[
                self.types_tanks.index(self.real_time_counter[1]) + 1]
        # Возвращаем тип танка, который в данный момент должен появиться
        return self.real_time_counter[1]

    def get_tile(self):
        from random import choice
        # Рандомно выбираем место для спавна бота
        tile = choice(self.free_tiles_for_spawn)
        em = EmptyBot(tile[0], tile[1],
                      self.game.TILE_SIZE, self.game.TILE_SIZE)
        if not pygame.sprite.spritecollide(em,
                                           self.game.all_sprites, False):
            return tile
        return False

    def set_target_for_bots(self, target):
        # Устанавливаем цель для всех ботов
        for i in self.game.mobs_group:
            i.set_target(target)

    def activate_bonus(self, name_bonus):
        # name_bonus = 'c' - clock, 'g'
        if name_bonus == 'c':
            for i in self.game.mobs_group:
                i.isFreeze = True
            self.bonus_timer = pygame.time.get_ticks()
            self.bonus_delay = 6000
            self.bonus_name = name_bonus
        if name_bonus == 'g':
            for i in self.game.mobs_group:
                i.kill()

    def check_bonuses(self):
        now = pygame.time.get_ticks()
        if self.bonus_timer is not None:
            if now - self.bonus_timer > self.bonus_delay:
                self.bonus_timer = None
                self.bonus_delay = None
                if self.bonus_name == 'c':
                    for i in self.game.mobs_group:
                        i.isFreeze = False
                    self.bonus_name = None


class Map:
    def __init__(self, path, map_size):
        # Т.к класс игры находится в одельной папке,
        # которая не лежит рядом c кодом, то нам приходится
        # настроить доступ к файлу
        os.chdir('..')
        self.map = pytmx.load_pygame(os.path.join(os.getcwd(), path))
        self.TILE_SIZE = map_size // self.map.width
        # Ширина и выстоа это количество клеток на карте
        self.width = self.map.width
        self.height = self.map.height
        # Коээфециент, который показывает насколько нужно
        # уменьшить размер клетки в частости и координаты
        self.koeff = self.map.tilewidth / self.TILE_SIZE
        # Квадрат - границы карты
        self.rect = pygame.rect.Rect((OFFSET, OFFSET),
                                     (MAP_SIZE, MAP_SIZE))
        # Получаем все слои из обекта карты и
        # проверяем наличие самых необходимых
        self.layers = list(self.map.layernames.keys())
        self.checking_layers()

    def checking_layers(self):
        """Проверка на наличие необходимых слоев"""
        for i in ['ground', 'spawn_players', 'spawn_bots', 'eagle']:
            if not self.check_(i):
                raise Exception(f'В карте не обнаружены необходимые слои: {i}')

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
        """Возвращает координаты клеток
         по id необходимой клетки из Tiled Map Edit"""
        return list(map(lambda x: convert_coords(x, self.TILE_SIZE),
                        self.map.get_tile_locations_by_gid(
            list(self.map.tiledgidmap.values()).index(id) + 1)))

    def render_layer(self, sc, layer_name: str):
        """Отрисовка на screen необходимых слоев"""
        # Узнаем имеется ли желаемый слой в списке доступных
        if layer_name not in self.layers:
            return
        layer = self.layers.index(layer_name)
        for x in range(self.width):
            for y in range(self.height):
                # По координате и номеру слоя отрисовываем тайл
                image = self.get_tile_image(x, y, layer)
                if image is not None:
                    sc.blit(image, (
                        x * self.TILE_SIZE + OFFSET,
                        y * self.TILE_SIZE + OFFSET))

    def check_(self, name):
        """Проверяет имеется ли слой в объекте карты"""
        return name in self.map.layernames

    def check_collide(self, rect: pygame.rect.Rect):
        """Проверка пересекает ли объект границы карты
        :param rect квадрат объекта с которым идет сравнение
        :return True если объект пересек границу
        :return False eсли объект не пересек границу"""
        if rect.y < self.rect.y or rect.x < self.rect.x \
                or rect.right > self.rect.right \
                or rect.bottom > self.rect.bottom:
            return True
        return False


class Game:
    def __init__(self, type_game, number_level):
        self.map = Map(f'{MAPDIR}map{number_level}.tmx', MAP_SIZE)
        self.map_object = self.map.map
        self.TILE_SIZE = self.map.TILE_SIZE
        self.MAP_SIZE = [OFFSET, OFFSET, MAP_SIZE + OFFSET, MAP_SIZE + OFFSET]
        self.type_game = type_game
        self.level = number_level

        self.isGameOver = False

        self.all_sprites = pygame.sprite.Group()
        self.mobs_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.map_group = pygame.sprite.Group()

        self.bullets = pygame.sprite.Group()
        self.bonus_group = pygame.sprite.Group()
        self.eagle = self.create_eagle()

        # Создаем спрайты стен
        self.create_walls()

        # для игроков ДОЛЖНО быть минимум и максимум 2
        # доступные клетки для спавна (В ДАННЫЙ МОМЕНТ УЧИТЫВАЕТСЯ
        # РЕЖИМ ЛИШЬ ТОЛЬКО НА 2 ЧЕЛОВЕК МАКСИМУМ)
        self.TILES_FOR_PLAYERS = self.map.get_tiled_by_id(TILE_FOR_PLAYERS)
        self.TILES_FOR_MOBS = self.map.get_tiled_by_id(TILE_FOR_MOBS)
        # print(self.TILES_FOR_PLAYERS)

        self.player1 = None
        self.player2 = None
        if type_game == 1 or type_game == 2:
            self.player1 = Player(self, self.TILES_FOR_PLAYERS[0],
                                  self.TILE_SIZE, player=1)
            if type_game == 2:
                self.player2 = Player(self, self.TILES_FOR_PLAYERS[1],
                                      self.TILE_SIZE, player=2)
        elif type_game == 3:
            raise Exception('Онлайн еще не готов')
        else:
            raise Exception('Неверный тип игры')
        self.bot_manager = BotManager(self)

    def create_walls(self):
        if not self.map.check_('walls'):
            return
        for i in self.map.get_objects('walls'):
            x, y = i.x / self.map.koeff + OFFSET, i.y / self.map.koeff + OFFSET
            wall = Wall(x, y, self.map.get_tile_id(i.gid), self.TILE_SIZE)
            wall.add(self.all_sprites, self.wall_group, self.map_group)

    def create_eagle(self):
        tile = self.map.get_objects('eagle')[0]
        x, y = tile.x / self.map.koeff + OFFSET, tile.y / self.map.koeff + OFFSET
        return Eagle(self, x, y, self.TILE_SIZE)

    def update(self, events=None):
        if self.eagle.isBroken:
            self.game_over()
        self.player_group.update(events)
        self.bullets.update()
        self.bonus_group.update()
        self.wall_group.update()
        self.bot_manager.update(events)

    def render(self):
        # Отрисовка по слоям.
        """
        Карта может содержать подобные слои.
        0. ground
        1. spawn_players
        2. spawn_bots
        3. trees
        """
        # Отрисовка земли
        self.map.render_layer(screen, 'ground')
        # render player and bullet and mobs
        self.all_sprites.draw(screen)
        self.bonus_group.draw(screen)
        # Отрисовка деревьев
        self.map.render_layer(screen, 'trees')

    def game_over(self):
        print('game_over')
        # quit()


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
                # print(pygame.key.name(event.key))
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(monitor_size,
                                                         pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(
                            (screen.get_width(), screen.get_height()),
                            pygame.RESIZABLE)
        game.update()
        game.render()

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
