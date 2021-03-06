import pytmx
import pygame
import os
from math import ceil
from modules.sprites import Player, Bot, Eagle, Wall, EmptyBot
from modules.default_funcs import load_image, load_settings
from random import choice

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
DIR_FOR_TANKS_IMG = 'tanks_texture\\'

MAP_SIZE = 650
OFFSET = 50

TILE_FOR_PLAYERS = 16
TILE_FOR_MOBS = 17


def set_constants_from_settings(screen_surf):
    global MAP_SIZE, OFFSET
    OFFSET = 40

    sc_w, sc_h = screen_surf.get_size()
    sc_w -= 2 * OFFSET
    sc_h -= 2 * OFFSET
    if sc_h <= sc_w:
        menue_w = (sc_h / 13) * 3
        size = sc_h + menue_w
        k = sc_w / size
        MAP_SIZE = int(sc_h * k) if k < 1 else sc_h
    if sc_h > sc_w:
        menue_w = (sc_w / 13) * 3
        size = sc_w + menue_w
        k = sc_w / size
        MAP_SIZE = int(sc_w * k) if k < 1 else sc_w


def convert_coords(x, tile_size):
    """Изменяем координаты в соответсвии со смещением"""
    return x[0] * tile_size + OFFSET, x[1] * tile_size + OFFSET, x[2]


def get_random_map_number():
    available_numbers = list(
        map(lambda x: int(x.split('.')[0].split('map')[-1]),
            filter(lambda x: x.endswith('.tmx'),
                   os.listdir(MAPDIR))))
    return choice(available_numbers)


class BotManager:
    def __init__(self, game_obj):
        self.game = game_obj
        # В зависимости от количества игроков на поле должно
        # быть или 4 или 6 вражеских танков
        self.player_count = 2 if self.game.player2 is not None \
            else 1 if self.game.player1 is not None else 0
        if self.player_count == 0:
            raise Exception('Недостаточно игроков')
        from modules import mobs_count
        """Загружаем шаблон, по которому будут спавниться боты"""
        try:
            # Если необходимого шаблона нет, то загружаем рандомный
            if self.game.real_level not in mobs_count.count:
                self.bot_comb = mobs_count.count[
                    choice(list(mobs_count.count.keys()))]
            else:
                self.bot_comb = mobs_count.count[self.game.real_level]
            # self.bot_comb = mobs_count.count[10]
        except KeyError:
            raise KeyError('Комбинация ботов не найдена')

        # Определяем время респавна ботов
        # (динамическое и зависит от уровня и количества игроков)
        self.respawn_time = (190 - self.game.level * 4 - (
                self.player_count - 1) * 60) * 12
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
        self.real_time_counter = [0, self.get_next_type()]
        self.visible_bots = 4 if self.player_count == 1 else 6
        # Устанавливаем клетки для спавна ботов
        self.free_tiles_for_spawn = self.game.TILES_FOR_MOBS

        self.bonus_timer = None
        self.bonus_delay = None
        self.bonus_name = None

    def get_count_bots(self):
        # Возвращает оставшееся количество незаспавненных ботов
        return self.global_count_bots

    def check_state(self):
        # Если все боты убиты, то игрок победил
        if len(self.game.mobs_group) <= 0 and self.global_count_bots <= 0:
            return True
        return False

    def update(self, events=None):
        now = pygame.time.get_ticks()
        self.check_bonuses()
        # Определяем убиты ли все боты. Если убиты, то игрок выйграл
        if self.check_state():
            return
        # Если игра продолжается, то мы создаем бота в
        # зависимости от времени респавна и количества ботов на карте
        if not self.game.isGameOver and \
                now - self.start_time > self.respawn_time and \
                len(self.game.mobs_group) < self.visible_bots \
                and self.global_count_bots > 0:
            tile = self.get_tile()
            # Если клетка для спавна свободна, то спавним бота
            if tile:
                Bot(self.game, tile,
                    self.game.TILE_SIZE, self.get_type_tank(),
                    sum(self.bot_comb) - self.global_count_bots)
                # Обновляем таймер спавна
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
        # Обновляем состояние всех ботов
        self.game.mobs_group.update(events)

    def get_next_type(self):
        # Возвращает следующий тип бота
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
        # Если место для спавна занять, то мы не можем заспавнить бота
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
        # Устанавливаем бонусы
        if name_bonus == 'c':
            for i in self.game.mobs_group:
                i.isFreeze = True
            self.bonus_timer = pygame.time.get_ticks()
            self.bonus_delay = 6000
            self.bonus_name = name_bonus
        if name_bonus == 'g':
            for i in self.game.mobs_group:
                i.kill(permanent=True)

    def check_bonuses(self):
        # Обновляем счетчик для бонусов
        now = pygame.time.get_ticks()
        if self.bonus_timer is not None:
            self.game.add_music_track({str(self.__class__.__name__): 'clock'})
            if now - self.bonus_timer > self.bonus_delay:
                # Если время действия бонуса закончилось, убираем счетчик
                self.bonus_timer = None
                self.bonus_delay = None
                if self.bonus_name == 'c':
                    # Если выпал бонус часы, то всех нужно и разморозить
                    for i in self.game.mobs_group:
                        i.isFreeze = False
                    self.bonus_name = None


class Map:
    def __init__(self, number_level, map_size):
        # Т.к класс игры находится в одельной папке,
        # которая не лежит рядом c кодом, то нам приходится
        # настроить доступ к файлу
        if os.getcwd().split('\\')[-1] == 'modules':
            os.chdir('..')
        # Загружаем уровень. Если нужного уровня не найдено, то
        # загружаем первый уровень
        self.level = number_level
        path = f'{MAPDIR}map{self.level}.tmx'
        if not os.path.isfile(path):
            self.level = get_random_map_number()
            path = f'{MAPDIR}map{self.level}.tmx'
        self.map = pytmx.load_pygame(os.path.join(os.getcwd(), path))
        # Размер клетки
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
        # Получение картинки тайла с изменнеными пропорциями
        image = self.map.get_tile_image(x, y, layer)
        if image is not None:
            image = pygame.transform.scale(image,
                                           (self.TILE_SIZE, self.TILE_SIZE))
            return image

    def get_objects(self, name):
        # Получаем названием обектов из объекта карты
        return self.map.layernames[name]

    def get_tile_id(self, gid):
        # Получаем id клетки по gid
        return self.map.tiledgidmap[gid]

    def get_tiled_by_id(self, id):
        """Возвращает координаты клеток
         по id необходимой клетки из Tiled Map Edit"""
        return list(map(lambda x: convert_coords(x, self.TILE_SIZE),
                        self.map.get_tile_locations_by_gid(
                            list(self.map.tiledgidmap.values()).index(
                                id) + 1)))

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
                or rect.right >= self.rect.right \
                or rect.bottom >= self.rect.bottom:
            return True
        return False


class Menu(pygame.sprite.Sprite):
    """
    Класс отвечающий за отриосвку меню (справа от поля)
    """
    images = {
        'bots': 'bots.png',
        'flag': 'level_flag.png',
        'p1': 'p1_v1.png',
        'p2': 'p2_v1.png',
        'pl': 'players.png'
    }

    def __init__(self, game):
        super().__init__(game.all_sprites)
        # Можно подключить какой-нибудь стиль для текста
        self.text_font = None
        self.game = game
        # Создаем разметку меню
        delta_x, delta_y = 30, self.game.MAP_SIZE.y
        self.rect = pygame.Rect(game.MAP_SIZE.width + delta_x, delta_y,
                                game.TILE_SIZE * 3, game.MAP_SIZE.height)
        # Вычисляем коэффейиенты для отрисовки
        self.m1 = self.game.TILE_SIZE / 2.8
        self.m2 = self.game.TILE_SIZE / 2
        self.m3 = self.game.TILE_SIZE
        # Подключаем все необходимые картики для отображение в меню
        self.bot_img = self.load_image('bots', self.m1)
        self.p = self.load_image('pl', self.m2)
        self.flag = self.load_image('flag', self.m3)
        # Если в игре участвуют два игрока, то необходимо
        # отрисовать количество жизней и у второго игрока
        self.is_two_pl = True if self.game.player2 is not None else False

        self.image = pygame.Surface((self.rect.width, self.rect.height),
                                    pygame.SRCALPHA, 32).convert_alpha()
        # Создание большинства шрифтов и рендер основного текста.
        self.font = pygame.font.Font(self.text_font, int(self.m3))
        self.f_nick = pygame.font.Font(self.text_font, int(self.m3 / 1.3))
        # Узнаем ники игроков
        self.p1_nick = self.f_nick.render(
            f"{self.game.pl_sett['first_player_nick']}",
            True, pygame.Color('black'))
        self.p2_nick = self.f_nick.render(
            f"{self.game.pl_sett['second_player_nick']}",
            True, pygame.Color('black'))

        self.level_text = self.font.render(
            f"{self.game.level}", True, pygame.Color('black'))

    def load_image(self, name, m):
        # Загрузка изображений менюшек
        image = load_image(f"{DIR_FOR_TANKS_IMG}\\menu\\{self.images[name]}")
        rect = image.get_rect()
        koeff = m / rect.height
        return pygame.transform.scale(image, (ceil(rect.width * koeff),
                                              ceil(rect.height * koeff)))

    def draw_bots_log(self):
        # Отрисовка количества оставшихся ботов
        count_bots = self.game.bot_manager.get_count_bots()
        x, y, w, h = self.bot_img.get_rect()
        org_x, c = x, 0
        for i in range(ceil(count_bots / 2)):
            for j in range(2):
                if c >= count_bots:
                    break
                self.image.blit(self.bot_img, (x, y, w, h))
                c += 1
                x += w + 4
            x = org_x
            y += h + 4

    def draw_players_log(self):
        # Отрисовка информации об игроках и номер уровня
        x = 0
        y = self.rect.height // 2

        # Узнаем количество жизней у игроков
        p1_lives = self.font.render(f"{self.game.player1.lives}", True,
                                    pygame.Color('black'))

        p2_lives = self.font.render(f"{self.game.player2.lives}", True,
                                    pygame.Color('black')) \
            if self.is_two_pl else None
        # Отрисовка ника игрока
        p_n_rect = self.p1_nick.get_rect()
        self.image.blit(self.p1_nick, (x, y, p_n_rect.width, p_n_rect.height))
        # Отрисовка мини-танчика игрока
        x, y = 0, y + p_n_rect.height + 6
        p_rc = self.p.get_rect()
        self.image.blit(self.p, (x, y, p_rc.width, p_rc.height))
        # Отрисовка жизни у первого игрока
        x, y = p_rc.width + 8, y - 3
        pl_lv = p1_lives.get_rect()
        self.image.blit(p1_lives, (x, y,
                                   pl_lv.width, pl_lv.height))
        # Если игра на двоих
        if self.is_two_pl:
            x, y = 0, y + pl_lv.height + 10
            # Отрисовка ника второго игрока
            p_n_rect = self.p2_nick.get_rect()
            self.image.blit(
                self.p2_nick, (x, y, p_n_rect.width, p_n_rect.height))
            # Отрисовка мини-танчика игрока
            x, y = 0, y + p_n_rect.height + 6
            p_rc = self.p.get_rect()
            self.image.blit(self.p, (x, y, p_rc.width, p_rc.height))
            # Отрисовка жизней второго игрока
            x, y = p_rc.width + 8, y - 3
            pl_lv = p2_lives.get_rect()
            self.image.blit(p2_lives, (x, y,
                                       pl_lv.width, pl_lv.height))
        # Отрисовка флага
        fl_rc = self.flag.get_rect()
        x, y = 0, self.rect.height - fl_rc.height * 3
        self.image.blit(self.flag, (x, y, fl_rc.width, fl_rc.height))
        # Отрисовка номера уровня
        x, y = x + fl_rc.width // 2, y + fl_rc.height // 1.5
        lev_rect = self.level_text.get_rect()
        self.image.blit(
            self.level_text, (x, y, lev_rect.width, lev_rect.height))

    def update(self, *args):
        # Обновление окна меню
        self.is_two_pl = True if self.game.player2 is not None else False
        self.image.fill(pygame.SRCALPHA)
        self.draw_bots_log()
        self.draw_players_log()


class PauseScreen:
    """
    Класс, который отвечает за отрисовку окна паузы
    """

    def __init__(self, game, screen):
        self.game = game
        self.pscreen = pygame.Surface((screen.get_rect().w,
                                       screen.get_rect().h),
                                      pygame.SRCALPHA, 32).convert()
        self.text_timer = pygame.time.get_ticks()
        font = pygame.font.Font(None, 50)
        self.text = font.render('PAUSE', False, (255, 255, 255, 255))

    def update(self):
        # Обновляем таймер для мигания текста
        now = pygame.time.get_ticks()
        if now - self.text_timer > 400:
            self.text.set_alpha(0 if self.text.get_alpha() in [
                None, 255] else 255)
            self.text_timer = now

    def render(self, screen):
        # Затемняем основной экран
        self.pscreen = pygame.transform.scale(self.pscreen, screen.get_size())
        self.pscreen.fill((150, 150, 150, 100))
        # Отрисовываем все необходимое
        screen.blit(self.pscreen, (0, 0),
                    special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(self.text, (self.pscreen.get_rect().w // 2
                                - self.text.get_rect().w // 2,
                                self.pscreen.get_rect().h // 3
                                - self.text.get_rect().h // 2))


class ConfirmWindow:
    def __init__(self, header_text, confirm_text, game):
        self.game = game
        self.WIDTH, self.HEIGHT = game.screen.get_size()
        self.header_text = header_text
        self.confirm_text = confirm_text

        self.width, self.height = int(
            0.187 * self.WIDTH), int(0.15 * self.HEIGHT)

        self.background = pygame.Surface((self.width, self.height)
                                         ).convert_alpha()
        self.top = pygame.Surface((self.width, self.height / 6)
                                  ).convert_alpha()

        self.top.fill((70, 70, 68))
        self.background.fill((147, 145, 142))
        self.window_scr = pygame.Surface((self.width, self.height)
                                         ).convert_alpha()

        font_head = pygame.font.SysFont("comicsans",
                                        round(0.015625 * self.WIDTH))
        font_conf = pygame.font.SysFont("comicsans",
                                        round(0.013 * self.WIDTH))
        self.header_text = font_head.render(self.header_text, True,
                                            (255, 255, 255))
        self.confirm_text = font_conf.render(self.confirm_text, True,
                                             (15, 15, 14))

        self.TS = self.game.TILE_SIZE
        self.k1 = self.TS
        self.k2 = self.TS // 2
        self.k3 = self.TS // 3
        self.exit_btn = Button('В меню', self.game,
                               int(self.WIDTH / 2 - 0.1 * self.WIDTH),
                               int(self.HEIGHT / 2 + 0.15 * self.HEIGHT / 4),
                               width=int(self.WIDTH * 0.1),
                               height=int(self.HEIGHT * 0.03),
                               size=20)
        self.cancel = Button('Отмена', self.game,
                             int(self.WIDTH / 2),
                             int(self.HEIGHT / 2 + 0.15 * self.HEIGHT / 4),
                             width=int(self.WIDTH * 0.1),
                             height=int(self.HEIGHT * 0.03),
                             size=20)

    def draw(self, win, mouse_pos=None):
        self.window_scr.blit(self.background, (0, 0))
        self.window_scr.blit(self.top, (0, 0))
        self.window_scr.blit(self.header_text, (
            (self.width - self.header_text.get_width()) / 2,
            self.height * 0.03))
        self.window_scr.blit(self.confirm_text, (
            (self.width - self.confirm_text.get_width()) / 2,
            self.height / 4.5))
        pygame.draw.line(self.window_scr, (57, 59, 61),
                         (0, self.height * 0.16),
                         (self.width, self.height * 0.16), 3)
        pygame.draw.rect(self.window_scr, (57, 59, 61),
                         (0, 0, self.width, self.height), 6)
        win.blit(self.window_scr,
                 ((self.WIDTH - self.width) / 2 + 2,
                  (self.HEIGHT - self.height) / 2))
        self.cancel.draw(win, mouse_pos)
        self.exit_btn.draw(win, mouse_pos)

    def update(self, mouse_state=None):
        if self.cancel.click(mouse_state):
            self.game.is_pause = False
            self.game.exit_menue_w = None
        elif self.exit_btn.click(mouse_state):
            self.game.set_feedback('exit')


class Button:
    """
    Класс кнопки
    """

    def __init__(self, text, game, x=0, y=0, width=616, height=68, size=40,
                 limit=(0, 0)):
        self.game = game
        self.text = text
        self.x = x
        self.y = y
        self.width, self.height = width, height
        self.limit_x = limit[0]
        self.limit_y = limit[1]
        self.size = size
        self.normal_image = self.hover_image = None
        self.load_img()
        font = pygame.font.SysFont("comicsans", self.size)
        self.text = font.render(self.text, True, (255, 255, 255))

    def set_text(self, text):
        self.text = text

    def set_coords(self, x, y):
        self.x, self.y = x, y

    def load_img(self):
        # if os.getcwd().split('\\')[-1] == 'modules':
        #     os.chdir('..')
        self.normal_image = pygame.transform.scale(
            load_image('tanks_texture/menu/button_normal.png'),
            (self.width, self.height))
        self.hover_image = pygame.transform.scale(
            load_image('tanks_texture/menu/button_hovered.png'),
            (self.width, self.height))

    def draw(self, win, mouse_pos):
        x1, y1 = mouse_pos
        # Узнаем позицию и отталкиваясь от этого реагируем как либо на это
        if self.x + self.limit_x <= x1 <= self.x + self.width - self.limit_x \
                and self.y <= y1 <= self.y + self.height:
            win.blit(self.hover_image, (self.x, self.y))
            win.blit(self.text, (self.x + self.width / 2 -
                                 self.text.get_width() / 2,
                                 self.y + self.height / 2 -
                                 self.text.get_height() / 1.65))
        else:
            win.blit(self.normal_image, (self.x, self.y))
            win.blit(self.text, (
                self.x + self.width / 2 - self.text.get_width() / 2,
                self.y + self.height / 2 - self.text.get_height() / 1.9))

    def click(self, mouse_state):
        # Обработка клика (если координаты мышки над нашей
        # кнопкой и был клик левой кнопкой мыши, то возвращаем True
        x1, y1 = mouse_state[0]
        is_click = mouse_state[1][0]
        if not is_click:
            return
        if (self.x + self.limit_x <= x1 <=
                self.x + self.width - self.limit_x and
                self.y <= y1 <= self.y + self.height):
            self.game.add_music_track('click')
            self.game.feedback = 'mouse_visible_false'
            return True
        else:
            return None


class GameOverScreen:
    """
    Класс отвечающий за окно после боя
    """
    images = {
        't1': 'tanks_texture/t1/t_w.png',
        't2': 'tanks_texture/t2/t_w.png',
        't3': 'tanks_texture/t3/t_w.png',
        't4': 'tanks_texture/t4/t_w.png',
    }

    def __init__(self, game, screen):
        self.game = game
        self.isWin = self.game.isWin
        self.screen = pygame.Surface((screen.get_rect().w,
                                      screen.get_rect().h),
                                     pygame.SRCALPHA, 32).convert_alpha()
        self.screen.fill((0, 0, 0))
        self.screen.set_alpha(0)
        self.max_alpha_screen = 215
        self.p1_nick = self.game.pl_sett['first_player_nick']
        self.p2_nick = self.game.pl_sett['second_player_nick']

        self.TS = self.game.TILE_SIZE
        self.tanks_img = self.load_tanks_img()

        # Установка коэффециентов
        self.k1 = self.TS
        self.k2 = self.TS // 2
        self.k3 = self.TS // 3
        # Содание кнопок
        self.action_btn = self.exit_btn = None
        self.can_move = True
        self.show_timer = pygame.time.get_ticks()
        self.show_delay = 2000

        self.log = {}
        self.load_log()

        font = pygame.font.Font(None, self.k1)
        self.font_log = pygame.font.Font(None, self.k2 + 15)
        self.rez_text = font.render('YOU WON' if self.isWin else "YOU LOSE",
                                    False, pygame.Color('red'))
        self.level = font.render(f"STAGE {self.game.level}",
                                 False, pygame.Color('orange'))
        self.p1_nick = font.render(self.p1_nick, False, pygame.Color('yellow'))
        self.p2_nick = font.render(self.p2_nick, False, pygame.Color('green'))

    def load_log(self):
        """Загружает информацию о количестве убитых игроками ботов
        а также формирует кнопки"""
        c = 0
        for player in [self.game.player1, self.game.player2]:
            c += 1
            if player is not None:
                points = player.count_points
                killed_enemies = player.killed_enemies
                self.log[c] = [points, killed_enemies]
        self.action_btn = Button('Продолжить' if self.isWin else "Повторить",
                                 self.game, width=5 * self.k1 + self.k2,
                                 height=self.k1, size=self.k2)
        self.exit_btn = Button('В главное меню', self.game,
                               width=5 * self.k1 + self.k2,
                               height=self.k1, size=self.k2)

    def update(self, mouse_state=None):
        now = pygame.time.get_ticks()
        # После установления результата игры некоторое время буздействуем
        if now - self.show_timer >= self.show_delay:
            self.can_move = False
        # Обработка нажатий на кнопки
        if self.action_btn.click(mouse_state):
            action = {'Продолжить': 'continue', 'Повторить': 'restart'}
            self.game.set_feedback(action[self.action_btn.text])
        elif self.exit_btn.click(mouse_state):
            self.game.set_feedback('exit')

    def render(self, screen, mouse_pos=None):
        """Отрисовка всей информации + кнопок"""
        self.screen = pygame.transform.scale(self.screen, screen.get_size())
        if self.can_move:
            return
        # Анимация плавного появления экрана
        self.screen.set_alpha(min(self.max_alpha_screen,
                                  self.screen.get_alpha() + 10))
        screen.blit(self.screen, (0, 0))
        if self.screen.get_alpha() < self.max_alpha_screen:
            return
        screen.blit(self.rez_text, (
            screen.get_width() // 2 - self.rez_text.get_width() // 2,
            self.TS - 10))
        screen.blit(self.level, (
            screen.get_width() // 2 - self.level.get_width() // 2,
            2 * self.TS))
        screen.blit(self.p1_nick, (
            screen.get_width() // 4 - self.p1_nick.get_width() // 2,
            2 * self.TS))
        if self.game.count_players == 2:
            screen.blit(self.p2_nick, (
                screen.get_width() * 3 // 4 - self.p2_nick.get_width() // 2,
                2 * self.TS))

        for i in range(len(self.tanks_img)):
            screen.blit(self.tanks_img[i],
                        (screen.get_width() // 2 -
                         self.tanks_img[i].get_width() // 2,
                         self.TS * 5 + (25 + self.TS) * i))

        sc_rect = screen.get_rect()
        w, h = sc_rect.w, sc_rect.h
        self.exit_btn.set_coords(w // 3 - self.exit_btn.width // 2,
                                 h - self.TS - self.exit_btn.height)
        self.action_btn.set_coords(w * 2 // 3 - self.exit_btn.width // 2,
                                   h - self.TS - self.exit_btn.height)

        self.action_btn.draw(screen, mouse_pos)
        self.exit_btn.draw(screen, mouse_pos)

        self.draw_log(screen)

    def draw_log(self, screen):
        """Отрисовка статистики"""
        x, y = screen.get_width() // 4, 3 * self.TS + 30
        y_orig = (self.TS * 5 + (25 + self.TS) * 4) + self.TS // 2

        for k in self.log.keys():
            data = self.log[k]
            if k != 1:
                x *= 3
            text = self.font_log.render(
                str(data[0]), False, pygame.Color('white'))
            screen.blit(text, (x - text.get_width() // 2, y))
            for t_t in data[1].keys():
                num_t = int(t_t[-1])
                y1 = (self.TS * 5 + (25 + self.TS) * (
                        num_t - 1)) + self.TS // 2
                score_text = self.font_log.render(f'Очки: {data[1][t_t][1]} - '
                                                  f'Кол-во: {data[1][t_t][0]}',
                                                  False, pygame.Color('white'))
                screen.blit(score_text, (x - score_text.get_width() // 2,
                                         y1 - score_text.get_height() // 2))
        result = self.font_log.render(
            f'TOTAL - {sum([i[0] for i in self.log.values()])}',
            False, pygame.Color('white'))
        screen.blit(result, (screen.get_width() // 2 - result.get_width() // 2,
                             y_orig))

    def load_tanks_img(self):
        """Загрузка изображения танков"""
        arr = []
        for i in ['t1', 't2', 't3', 't4']:
            img = load_image(self.images[i])
            arr.append(pygame.transform.scale(img, (self.TS, self.TS)))
        return arr.copy()


class Game:
    def __init__(self, type_game, number_level, screen_surf):
        set_constants_from_settings(screen_surf)

        self.map = Map(number_level, MAP_SIZE)
        self.map_object = self.map.map
        self.TILE_SIZE = self.map.TILE_SIZE
        self.MAP_SIZE = pygame.Rect(OFFSET, OFFSET,
                                    MAP_SIZE + OFFSET, MAP_SIZE + OFFSET)
        self.type_game = type_game
        self.real_level = number_level
        self.level = self.map.level
        self.track_list = []

        self.pl_sett = load_settings()['player_settings']
        self.screen = screen_surf
        self.game_over_screen = None
        self.feedback = None
        self.pause_screen = PauseScreen(self, self.screen)
        self.pause_sc_timer = pygame.time.get_ticks()
        self.is_pause = self.isGameOver = False
        self.isWin = None
        self.exit_menue_w = None
        self.is_music_changed = [False, False]

        self.all_sprites = pygame.sprite.Group()
        self.mobs_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.map_group = pygame.sprite.Group()
        self.animation_sprite = pygame.sprite.Group()

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
        self.count_players = 1 if self.player2 is None else 2
        self.bot_manager = BotManager(self)
        self.menu = Menu(self)

    def create_walls(self):
        # Если на карте есть стены, то мы должны их создать в
        # качестве объектов и добавить в группу стен
        if not self.map.check_('walls'):
            return
        for i in self.map.get_objects('walls'):
            x = (i.x / self.map.koeff) + OFFSET
            y = (i.y / self.map.koeff) + OFFSET
            Wall(x, y, self.map.get_tile_id(i.gid),
                 self.TILE_SIZE, self)

    def create_eagle(self):
        # Создаем объект орла
        tile = self.map.get_objects('eagle')[0]
        x = tile.x / self.map.koeff + OFFSET
        y = tile.y / self.map.koeff + OFFSET
        return Eagle(self, x, y, self.TILE_SIZE)

    def update(self, events=None, keystate=None, mouse_state=None):
        # Обновляем каждый элемент в игре
        if events is not None:
            # Если нажали кнопку паузы, то необходимо
            # остановить обновление объектов игры
            if events.type == pygame.KEYDOWN:
                if events.key == pygame.K_p:
                    self.is_pause = not self.is_pause
                    self.exit_menue_w = None
                    self.feedback = 'mouse_visible_true' if \
                        self.is_pause else 'mouse_visible_false'
                if events.key == pygame.K_ESCAPE and not self.isGameOver:
                    if self.exit_menue_w is None:
                        self.is_pause = True
                        self.exit_menue_w = ConfirmWindow(
                            'Выйти в меню?', 'Действительно выйти в меню?',
                            self)
                    else:
                        self.is_pause = False
                        self.exit_menue_w = None
                    self.feedback = 'mouse_visible_true' if \
                        self.is_pause else 'mouse_visible_false'
            return
        if not self.is_pause:
            # Если игра проиграна, то необходимо отрисовать окно проигрыша
            if self.isGameOver:
                self.game_over(mouse_state)
                if not self.game_over_screen.can_move:
                    return
            if any(map(lambda x: not x, self.is_music_changed)):
                if self.bot_manager.get_count_bots() < 5 \
                        and not self.is_music_changed[1]:
                    self.add_music_track({'change_music': 'bg3'})
                    self.is_music_changed[1] = True
                elif self.bot_manager.get_count_bots() < 10 \
                        and not self.is_music_changed[0]:
                    self.add_music_track({'change_music': 'bg2'})
                    self.is_music_changed[0] = True
            self.player_group.update(events, keystate=keystate)
            self.bullets.update()
            self.wall_group.update()
            self.bot_manager.update(events)
            self.bonus_group.update()
            self.animation_sprite.update()
            self.menu.update()
            # Проверка проиграна ли игра или выйграна
            self.is_game_over()
        else:
            self.pause_screen.update()
            if self.exit_menue_w is not None:
                self.exit_menue_w.update(mouse_state)

    def render(self, mouse_pos=None):
        # Отрисовка по слоям.
        """
        Карта может содержать подобные слои.
        0. ground
        1. spawn_players
        2. spawn_bots
        3. trees
        """
        self.screen.fill(pygame.Color(115, 117, 115))
        # Отрисовка земли
        self.map.render_layer(self.screen, 'ground')
        # render player and bullet and mobs
        self.all_sprites.draw(self.screen)
        # Отрисовка деревьев
        self.map.render_layer(self.screen, 'trees')
        self.bonus_group.draw(self.screen)
        self.animation_sprite.draw(self.screen)

        if self.is_pause:
            self.pause_screen.render(self.screen)
            if self.exit_menue_w is not None:
                self.exit_menue_w.draw(self.screen, mouse_pos)
        if self.isGameOver:
            self.game_over_screen.render(self.screen, mouse_pos=mouse_pos)

    def is_game_over(self):
        # Если иничтожены все боты-враги, то игры выйграна
        # Если все жизни игрока потрачены или уничтожен орел, то игра проиграна
        if not self.isGameOver:
            if self.bot_manager.check_state():
                self.isWin = True
                self.isGameOver = True
            elif all(map(lambda x: not x.alive(), self.player_group)) or \
                    self.eagle.isBroken:
                self.isWin = False
                self.isGameOver = True
            if self.isWin is not None:
                self.add_music_track({
                    'change_music': 'won' if self.isWin else 'lost'})
            if self.isGameOver:
                self.game_over_screen = GameOverScreen(self, self.screen)
                self.feedback = 'mouse_visible_true'

    def set_feedback(self, name):
        self.feedback = name

    def game_over(self, mouse_state):
        self.game_over_screen.update(mouse_state=mouse_state)

    def add_music_track(self, name):
        # Добавляет название трека в списко треков
        self.track_list.append(name)

    def get_track_list(self):
        # Возвращает списко с названиями треков. После чего очищает себя
        tr_ls = self.track_list.copy()
        self.track_list.clear()
        return tr_ls

    def get_players_data_for_next_game(self):
        data = {}
        for i in self.player_group:
            data[i.player] = [i.lives, i.type_tanks]
        return data

    def set_players_data(self, data):
        for i in self.player_group:
            if i.player in data:
                i.lives = data[i.player][0]
                i.type_tanks = data[i.player][1]
                i.set_properties()
