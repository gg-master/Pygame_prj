import pygame
from settings import *
from random import random, choice, randrange
from default_funcs import load_image

DIR_FOR_TANKS_IMG = 'tanks_texture\\'
WORLDIMG_DIR = 'world\\'
WIDTH, HEIGHT = 950, 750
MAP_SIZE = 650
OFFSET = 50
FPS = 60


class Player(pygame.sprite.Sprite):
    images = {
        '1_t0': 't_y.png', '1_l0': 't_y_l.png', '1_r0': 't_y_r.png',
        '1_b0': 't_y_b.png',
        '1_t1': 't_y1.png', '1_l1': 't_y1_l.png', '1_r1': 't_y1_r.png',
        '1_b1': 't_y1_b.png',
        '2_t0': 't_g.png', '2_l0': 't_g_l.png', '2_r0': 't_g_r.png',
        '2_b0': 't_g_b.png',
        '2_t1': 't_g1.png', '2_l1': 't_g1_l.png', '2_r1': 't_g1_r.png',
        '2_b1': 't_g1_b.png',
    }

    def __init__(self, game, coords, tile_size, player):
        super().__init__(game.player_group, game.map_group, game.all_sprites)
        self.game = game
        self.side = 't'
        self.player = player
        self.type_tanks = 't1'
        self.move_trigger = False

        self.killed_enemies = {}
        self.count_points = 0

        self.speed = 2
        self.lives = 3

        self.bullet = None
        self.bullet_speed = 5
        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()

        self.hidden = self.with_shield = self.spawn_stopper = False
        self.set_properties()

        self.TILE_SIZE = tile_size
        self.mask = self.image = None
        self.load_tanks_image()

        self.coords = coords
        self.rect = self.image.get_rect()
        self.none_image = pygame.Surface((self.rect.width, self.rect.height),
                                         pygame.SRCALPHA, 32)
        self.orig_image = self.image.copy()
        self.spawn()

    def spawn(self):
        self.hidden = True
        self.with_shield = True
        self.spawn_stopper = True
        Shield(self)
        SpawnAnim(self)
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

    def activate_bonus(self, name_bonus):
        # name_bonus = 's' - star, 'h' - helmet, 't' - tank, 'p' - pistol
        if name_bonus == 's':
            self.type_tanks = f't{min(4, int(self.type_tanks[1]) + 1)}'
            self.set_properties()
        elif name_bonus == 't':
            self.lives += 1
        elif name_bonus == 'h':
            self.with_shield = True
            Shield(self)
        elif name_bonus == 'p':
            self.type_tanks = 't4'
            self.lives += 2
            self.set_properties()

    def set_properties(self):
        if self.type_tanks == 't1':
            self.speed = 2
        elif self.type_tanks == 't2':
            self.speed = 3
            self.bullet_speed = 6
        elif self.type_tanks == 't3':
            self.bullet_speed = 7

    def load_tanks_image(self):
        self.move_trigger = not self.move_trigger
        name_img = f"{self.player}_{self.side}{int(self.move_trigger)}"
        image = load_image(f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{self.images[name_img]}')
        self.image = pygame.transform.scale(image, (self.TILE_SIZE -
                                                    self.TILE_SIZE // 8,
                                                    self.TILE_SIZE -
                                                    self.TILE_SIZE // 8))
        s = pygame.Surface((self.image.get_rect().width,
                            self.image.get_rect().height), pygame.SRCALPHA)
        s.fill(pygame.color.Color('black'))
        self.mask = pygame.mask.from_surface(s)

    def kill(self):
        if not self.with_shield:
            Explosion(self)
            if self.lives < 0:
                self.game.game_over()
                self.hidden = True
                return
            if self.type_tanks == 't4':
                # TODO прописать особенность для танка 4
                #  типа у игрока при убийстве
                pass
            # self.lives -= 1
            # self.spawn()

    def move_collide(self, side: str, speed=(0, 0)):
        self.side = side
        self.load_tanks_image()
        self.rect = self.rect.move(speed[0], speed[1])
        c = pygame.sprite.spritecollide(self, self.game.map_group, False,
                                        pygame.sprite.collide_mask)
        c_b = pygame.sprite.spritecollideany(self, self.game.bonus_group)
        c_b.activate_bonus(self) if c_b else ''
        del c[c.index(self)]
        # TODO обработка столкновений с другими игроками и тд
        """За обработку столкновений с пулями отвечает сама пуля"""
        if self.game.map.check_collide(self.rect) or c:
            self.rect = self.rect.move(-speed[0], -speed[1])

    def move(self, keystate, obj):
        if keystate[pygame.key.key_code(obj['up'])]:
            self.move_collide('t', (0, -self.speed))
        elif keystate[pygame.key.key_code(obj['down'])]:
            self.move_collide('b', (0, self.speed))
        elif keystate[pygame.key.key_code(obj['left'])]:
            self.move_collide('l', (-self.speed, 0))
        elif keystate[pygame.key.key_code(obj['right'])]:
            self.move_collide('r', (self.speed, 0))

    def update(self, *args):
        if self.hidden:
            self.image = self.none_image
            return
        elif not self.hidden and self.spawn_stopper:
            self.image = self.orig_image
            self.spawn_stopper = False

        # TODO При игре по сети необходимо как то получать нажатые клавиши
        keystate = pygame.key.get_pressed()
        if self.player == 1:
            obj = PLAYER1
        else:
            obj = PLAYER2

        self.move(keystate, obj)
        if keystate[pygame.key.key_code(obj['shoot'])]:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.bullet is None or not self.bullet.alive():
                bullet = Bullet(self.rect, self.side, self.game, self,
                                speed=self.bullet_speed)
                bullet.add(self.game.all_sprites, self.game.bullets)
                self.bullet = bullet

    def earn_points(self, mob):
        # mob - points
        points = mob.points
        PointsAnim(self.game, points, mob.rect)
        self.count_points += points
        if mob.__class__.__name__ == 'Bot':
            type_b = mob.type_tanks
            if type_b not in self.killed_enemies:
                self.killed_enemies[type_b] = points
            else:
                self.killed_enemies[type_b] += points

    def compare_rect_with_bot(self, rect: pygame.rect.Rect):
        if rect.x <= self.rect.x <= rect.x + rect.width\
                or rect.y <= self.rect.y <= rect.y + rect.width:
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    images = {
        't': 'b.png',
        'l': 'b_l.png',
        'r': 'b_r.png',
        'b': 'b_b.png'
    }

    def __init__(self, rect_tank, side: str, game, who_shoot, speed=5):
        super().__init__()
        self.who_shoot = who_shoot
        self.game = game
        self.image = load_image(f'{DIR_FOR_TANKS_IMG}'
                                f'bullet\\{self.images[side]}')
        k = (rect_tank.width // 4) // self.image.get_rect().width
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_rect().width * k,
                                             self.image.get_rect().height * k))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.side = side
        self.speed = speed
        self.speedy, self.speedx = 0, 0
        self.set_rect(rect_tank)

    def update(self, *event):
        self.rect = self.rect.move(self.speedx, self.speedy)
        # удалить спрайт, если он заходит за верхнюю часть экрана
        if self.game.map.check_collide(self.rect):
            self.kill()
        # TODO столкновне с другими пулями, игроками
        c = pygame.sprite.spritecollideany(self, self.game.all_sprites)
        if c is not None:
            if c in self.game.wall_group and c.isWall:
                coord_collide = pygame.sprite.collide_mask(c, self)
                if coord_collide is not None:
                    if c.isBroken:
                        c.change_yourself(coord_collide)
                    self.kill()
            if c in self.game.player_group:
                if self.who_shoot != c:
                    c.kill()
                    self.kill()
            if c in self.game.bullets and c is not self:
                if self.who_shoot.__class__ != c.who_shoot.__class__:
                    self.kill()
                    c.kill()
            if c in self.game.mobs_group and \
                    self.who_shoot.__class__ == Player:
                self.who_shoot.earn_points(c)
                c.kill()
                self.kill()
            if c == self.game.eagle:
                c.eagle_break()
                self.kill()

    def kill(self):
        Explosion(self)
        super().kill()

    def set_rect(self, rect_tank):
        if self.side == 't':
            self.rect.top = rect_tank.top  # self.rect.bottom
            self.rect.centerx = rect_tank.centerx
            self.speedy = -self.speed
        if self.side == 'l':
            self.rect.left = rect_tank.left  # self.rect.right
            self.rect.centery = rect_tank.centery
            self.speedx = -self.speed
        if self.side == 'r':
            self.rect.right = rect_tank.right  # self.rect.left
            self.rect.centery = rect_tank.centery
            self.speedx = self.speed
        if self.side == 'b':
            self.rect.bottom = rect_tank.bottom  # self.rect.top
            self.rect.centerx = rect_tank.centerx
            self.speedy = self.speed


class EmptyBot(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.mask = pygame.mask.from_surface(
            pygame.Surface((self.rect.width, self.rect.height)))


class Bot(pygame.sprite.Sprite):
    images = {
        't0': 't_w.png', 'l0': 't_w_l.png', 'r0': 't_w_r.png',
        'b0': 't_w_b.png',
        't1': 't_w1.png', 'l1': 't_w1_l.png', 'r1': 't_w1_r.png',
        'b1': 't_w1_b.png',
        't00': 't_r.png', 'l00': 't_r_l.png', 'r00': 't_r_r.png',
        'b00': 't_r_b.png',
        't11': 't_r1.png', 'l11': 't_r1_l.png', 'r11': 't_r1_r.png',
        'b11': 't_r1_b.png',
        't0_4': 't_g.png', 'l0_4': 't_g_l.png', 'r0_4': 't_g_r.png',
        'b0_4': 't_g_b.png',
        't1_4': 't_g1.png', 'l1_4': 't_g1_l.png', 'r1_4': 't_g1_r.png',
        'b1_4': 't_g1_b.png',
        't0_3': 't_y.png', 'l0_3': 't_y_l.png', 'r0_3': 't_y_r.png',
        'b0_3': 't_y_b.png',
        't1_3': 't_y1.png', 'l1_3': 't_y1_l.png', 'r1_3': 't_y1_r.png',
        'b1_3': 't_y1_b.png'
    }

    def __init__(self, game, coords, tile_size, type_bot: str, number_tank):
        super().__init__(game.map_group, game.mobs_group, game.all_sprites)

        self.game = game
        self.type_tanks = type_bot
        self.number = number_tank
        self.side = 't'
        self.prev_side = 't'
        self.available_side = ['t', 'l', 'b', 'r']
        self.sides_flags = [False, False, False, False]
        self.is_stop_y = self.is_stop_x = False

        self.move_trigger = self.is_bonus = self.bonus_trigger = False
        self.bonus_trigger_delay = 300
        self.bonus_trigger_timer = pygame.time.get_ticks()
        self.trigger_image = 3

        self.isFreeze = self.spawn_stopper = self.hidden = False

        self.speed = 2
        self.speedx = self.speedy = 0

        self.lives = 1

        self.can_shoot = True
        self.bullet = None
        self.bullet_speed = 5
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()

        self.start_time = pygame.time.get_ticks()
        self.change_side_timer = 2000

        self.target = None
        self.points = 100

        self.set_properties()

        self.TILE_SIZE = tile_size
        self.image = self.mask = None
        self.load_tanks_image()

        self.coords = coords
        self.rect = self.image.get_rect()
        self.none_image = pygame.Surface((self.rect.width, self.rect.height),
                                         pygame.SRCALPHA, 32)
        self.orig_image = self.image.copy()
        self.spawn()

    def spawn(self):
        self.hidden = True
        self.spawn_stopper = True
        SpawnAnim(self)
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

    def update(self, *event):
        if self.hidden:
            self.image = self.none_image
            return
        elif not self.hidden and self.spawn_stopper:
            self.image = self.orig_image
            self.spawn_stopper = False
        if not self.isFreeze and not self.hidden:
            self.move()
            self.shoot()

    def kill(self):
        if self.lives > 1:
            self.lives -= 1
            return
        if self.is_bonus:
            Bonus(self.game)
        Explosion(self)
        super().kill()

    def set_properties(self):
        self.isFreeze = False if\
            self.game.bot_manager.bonus_delay is None else True
        if self.number in [4, 11, 18]:
            self.is_bonus = True
        if self.type_tanks == 't1':
            self.speed = 1
        elif self.type_tanks == 't2':
            self.speed = 3
            self.points = 200
        elif self.type_tanks == 't3':
            self.bullet_speed = 7
            self.points = 300
        elif self.type_tanks == 't4':
            self.lives = 4
            self.points = 400

    def set_target(self, target):
        self.target = target

    def get_image_name(self):
        now = pygame.time.get_ticks()
        name = f"{self.side}{int(self.move_trigger)}"
        if 2 < self.lives <= 4:
            name = f'{self.side}{int(self.move_trigger)}_{self.lives}'
        elif self.lives == 2:
            name = f"{self.side}{int(self.move_trigger)}_{self.trigger_image}"
        """Если у нас танк является бонусным, то он должен мигать"""
        if now - self.bonus_trigger_timer > self.bonus_trigger_delay and \
                self.is_bonus:
            if now - self.bonus_trigger_timer > self.bonus_trigger_delay * 2:
                self.bonus_trigger_timer = now
            name = f"{self.side}{int(self.move_trigger)}" \
                f"{int(self.move_trigger)}"
        return name

    def load_tanks_image(self):
        self.move_trigger = not self.move_trigger
        if self.is_bonus:
            self.bonus_trigger = not self.bonus_trigger
        self.trigger_image = 4 if self.trigger_image == 3 else 3

        name_image = self.images[self.get_image_name()]
        image = load_image(f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{name_image}')
        self.image = pygame.transform.scale(image, (self.TILE_SIZE -
                                                    self.TILE_SIZE // 8,
                                                    self.TILE_SIZE -
                                                    self.TILE_SIZE // 8))
        s = pygame.Surface((self.image.get_rect().width,
                            self.image.get_rect().height), pygame.SRCALPHA)
        s.fill(pygame.color.Color('black'))
        self.mask = pygame.mask.from_surface(s)

    def set_speedxy(self):
        speeds = {'r': [self.speed, 0],
                  'l': [-self.speed, 0],
                  't': [0, -self.speed],
                  'b': [0, self.speed]}
        self.speedx, self.speedy = speeds[self.side]

    def get_side(self, direction):
        if direction == 1:
            index = self.available_side.index(self.side)
            if index == len(self.available_side) - 1:
                return self.available_side[0]
            return self.available_side[index + 1]
        elif direction == -1:
            index = self.available_side.index(self.side)
            if index == len(self.available_side) - 1:
                return self.available_side[-1]
            return self.available_side[index - 1]

    def change_side(self, custom=False):
        anti_side = {"r": 'l', 'l': 'r', 't': 'b', 'b': 't'}
        if custom:
            if random() > 0.5:
                self.side = self.get_side(direction=1)
            else:
                self.side = self.get_side(direction=-1)
            return

        if random() < 0.20:  # 0.25
            self.side = anti_side[self.side]
        else:
            if random() < 0.5:  # 0.5
                self.side = anti_side[self.side]
            else:
                if random() > 0.5:
                    self.side = self.get_side(direction=1)
                else:
                    self.side = self.get_side(direction=-1)
        self.set_speedxy()

    def move_collide(self, side: str, speed=(0, 0)):
        self.side = side
        self.load_tanks_image()
        self.rect = self.rect.move(speed[0], speed[1])
        c = pygame.sprite.spritecollide(self, self.game.map_group, False,
                                        pygame.sprite.collide_mask)
        del c[c.index(self)]
        if c or self.game.map.check_collide(self.rect):
            self.rect = self.rect.move(-speed[0], -speed[1])
            if self.target is None:
                self.change_side()
            if self.target is not None:
                return False, None if not c else c[0]

    def get_nearest_players(self):
        def hypot(x1, y1, x2, y2):
            return (abs(x1 - x2) + abs(y1 - y2)) ** 0.5
        lens = {}
        for i in self.game.player_group:
            lens[hypot(i.rect.x, i.rect.y, self.rect.x, self.rect.y)] = i
        pl = lens[min(list(lens.keys()))]
        return pl.rect

    def check_pos_by_emptbot(self, pref_side):
        """С помощью 'пустого бота' (имеет только rect и mask) мы проверяем,
         можем ли заехать на определенную клетку"""
        speeds = {'r': [self.speed, 0], 'l': [-self.speed, 0],
                  't': [0, -self.speed], 'b': [0, self.speed]}
        empty_b = EmptyBot(self.rect.x, self.rect.y,
                           self.rect.width, self.rect.height)
        empty_b.rect = empty_b.rect.move(speeds[pref_side])
        c = pygame.sprite.spritecollide(empty_b, self.game.map_group, False,
                                        pygame.sprite.collide_mask)
        del c[c.index(self)]
        if c:
            return False
        return True

    def check_side(self, pref_side):
        """Функция, которая узнает может ли бот проехать в позицию pref_side,
         т.е в том направлении, в котором расположен игрок.
         Но если мы однажды не смогли проехать в том направлении
          (об этом мы узнаем из поля side_flags,
          где показывается в какую сторону мы не смогли проехать)
         То мы едем и смотрим можем ли проехать в позицию prev_side
         (т.е та, в которую ехали раньше)
            Допустим pref_side = 'b'
                     prev_side = 'b'
                     side = 'l
                Т.е мы едем влево, но хотим ехать вниз, то при каждом
                передвижении мы проверяем можем ли мы проехать вниз,
                и если можем, то изменяем side и prev_side, т.е поворачиваем"""
        anti_side = {'r': 'l', 'l': 'r', 't': 'b', 'b': 't'}
        if self.check_pos_by_emptbot(pref_side):
            if self.sides_flags[self.available_side.index(pref_side)]:
                is_empty = self.check_pos_by_emptbot(self.prev_side)
                if is_empty:
                    if self.prev_side in ['t', 'b']:
                        if self.side in ['r', 'l']:
                            s = self.side
                            self.side = self.prev_side
                            self.prev_side = anti_side[s]
                            return False
                    elif self.prev_side in ['r', 'l']:
                        if self.side in ['b', 't']:
                            s = self.side
                            self.side = self.prev_side
                            self.prev_side = anti_side[s]
                            return False
            elif not self.sides_flags[self.available_side.index(pref_side)]:
                return True
        return False

    def get_side_by_pos(self, target_rect):
        if abs(target_rect.centerx - self.rect.centerx) > abs(
                target_rect.centery - self.rect.centery):
            if target_rect.centerx >= self.rect.centerx:
                return 'r'
            if target_rect.centerx <= self.rect.centerx:
                return 'l'
        else:
            if target_rect.centery >= self.rect.centery:
                return 'b'
            if target_rect.centery <= self.rect.centery:
                return 't'

    def move(self):
        def just_drive():
            self.set_speedxy()
            now = pygame.time.get_ticks()
            self.move_collide(self.side, (self.speedx, self.speedy))
            if now - self.start_time > self.change_side_timer:
                self.change_side(custom=True)
                self.start_time = now

        def go_to(target_rect):
            # Узнаем сторону, в которую нам предпочтительно ехать
            pref_side = self.get_preferred_side(target_rect)
            # Если стороны нет (т.е мы приехали, то останавливаемся)
            if pref_side is None:
                self.move_collide(self.get_side_by_pos(target_rect), (0, 0))
                return
            rez = self.check_side(pref_side)
            if rez:
                self.side = pref_side
            # print(self.side, self.prev_side,
            #       pref_side, '-', self.sides_flags,
            #       (self.is_stop_x, self.is_stop_y), rez)
            self.set_speedxy()
            rez = self.move_collide(self.side, [self.speedx, self.speedy])
            if rez is not None and not rez[0]:
                if rez[1] is not None and\
                        rez[1].__class__.__name__ == 'Wall' and\
                        rez[1].isBroken and random() < 1 / 3:
                    self.shoot(custom=True)
                    return
                else:
                    self.sides_flags[
                        self.available_side.index(self.side)] = True
                    self.breaking_deadlock()
            else:
                self.sides_flags[self.available_side.index(self.side)] = False

        if self.target is None:
            just_drive()
        if self.target == 'players':
            # Узнаем позицию цели
            players_rect = self.get_nearest_players()
            go_to(players_rect)
        if self.target == 'eagle':
            rect = self.game.eagle.rect
            go_to(rect)

    def shoot(self, custom=False):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.can_shoot and (self.bullet is None or
                                   not self.bullet.alive()):
                if random() < 1 / 10 or self.compare_rect() or custom:
                    bullet = Bullet(self.rect, self.side, self.game, self,
                                    speed=self.bullet_speed)
                    bullet.add(self.game.all_sprites, self.game.bullets)
                    self.bullet = bullet

    def compare_rect(self):
        """Сравнивает координаты с орлом и игроком.
        При равестве стреляет"""
        for i in self.game.player_group:
            if i.compare_rect_with_bot(self.rect):
                return True
        if self.game.eagle.compare_rect_with_bot(self.rect):
            return True
        return False

    def get_preferred_side(self, players_rect):
        """Функция, которая в зависимости от расположения
         игрока к боту определяет сторону, в которую необходимо ехать боту"""
        # TODO доп.комментарии
        p_x, p_y = players_rect.centerx, players_rect.centery
        b_x, b_y = self.rect.centerx, self.rect.centery
        """Если мы достагли цели 
        (одинаковые центральные координаты или координаты сторон одинаковы)
        то останавливаемся"""
        if (p_x == b_x and b_y == p_y) or \
            (players_rect.left == self.rect.right and
                players_rect.top <= b_y <= players_rect.bottom) or\
            (players_rect.right == self.rect.left and
                players_rect.top <= b_y <= players_rect.bottom) or\
            (players_rect.top == self.rect.bottom and
                players_rect.left <= b_x <= players_rect.right) or\
            (players_rect.bottom == self.rect.top and
                players_rect.left <= b_x <= players_rect.right):
            self.is_stop_y = False
            self.is_stop_x = False
            return None
        # Если игрок ниже бота, то говорим боту передвигаться вниз
        if p_y >= b_y and not self.is_stop_y:
            if not (p_y - self.speed <= b_y <= p_y + self.speed):
                return 'b'
            # Если спустились настолько,
            # что мы на одной координате по y (при этом цель не достигнули)
            # то говорим, что мы уперлись по координате y (is_stop_y)
            # и теперь передвигаемся по координате x
            self.is_stop_y = True
            self.is_stop_x = False
        elif p_y <= b_y and not self.is_stop_y:
            if not (p_y - self.speed <= b_y <= p_y + self.speed):
                return 't'
            self.is_stop_y = True
            self.is_stop_x = False
        if p_x >= b_x:
            if not (p_x - self.speed <= b_x <= p_x + self.speed):
                return 'r'
            # Аналогично что и для координаты y. Если вышли на одну
            # координату, то говорим, что мы уперлись,
            # и теперь необходимо передвигаться по Y
            # В данный момент не используется по причине того,
            # что сначала идет проверка по Y,
            # и в любом случае мы сначала будем двигаться по Y
            self.is_stop_y = False
            self.is_stop_x = True
        elif p_x <= b_x:
            if not (p_x - self.speed <= b_x <= p_x + self.speed):
                return 'l'
            self.is_stop_y = False
            self.is_stop_x = True
            return
        return None

    def breaking_deadlock(self):
        # TODO доп.комментарии
        anti_side = {'r': 'l', 'l': 'r', 't': 'b', 'b': 't'}
        if self.side == 'b':
            if self.prev_side in [anti_side[self.side], 'b']:
                self.side = 'l' if random() < 1 / 2 else 'r'
                self.prev_side = 'b'
                return
            else:
                if random() < 1 / 2:
                    self.side = anti_side[self.prev_side]
                    self.prev_side = 'b'
                    return
                else:
                    self.side = 't'
                    return
        if self.side == 't':
            if self.prev_side in [anti_side[self.side], 't']:
                self.side = 'l' if random() < 1 / 2 else 'r'
                self.prev_side = 't'
                return
            else:
                if random() < 1 / 2:
                    self.side = anti_side[self.prev_side]
                    self.prev_side = 't'
                    return
                else:
                    self.side = 'b'
                    return
        if self.side == 'l':
            if self.prev_side == self.side:
                self.side = 't' if random() < 1 / 2 else 'b'
                self.prev_side = 'l'
                return
            else:
                if random() < 1 / 2:
                    self.side = 't' if self.prev_side == 'b' else 'b'
                    self.prev_side = 'l'
                    return
                else:
                    self.side = 'r'
                    self.prev_side = 'b'
                    return
        if self.side == 'r':
            if self.prev_side == self.side:
                self.side = 't' if random() < 1 / 2 else 'b'
                self.prev_side = 'b'
                return
            else:
                if random() < 1 / 2:
                    self.side = 't' if self.prev_side == 'b' else 'b'
                    self.prev_side = 'r'
                    return
                else:
                    self.side = 'l'
                    self.prev_side = 'b'
                    return


class Eagle(pygame.sprite.Sprite):
    images = {
        'normal': 'eagle.png',
        'broken': 'eagle_broken.png'
    }

    def __init__(self, game, x, y, tile_size):
        super().__init__(game.all_sprites, game.map_group)
        self.TILE_SIZE = tile_size
        self.image = load_image(f'{WORLDIMG_DIR}{self.images["normal"]}')
        self.image = pygame.transform.scale(self.image, (self.TILE_SIZE,
                                                         self.TILE_SIZE))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = x
        self.rect.y = y
        self.game = game
        self.isBroken = False

    def eagle_break(self):
        self.image = load_image(f'{WORLDIMG_DIR}\\{self.images["broken"]}')
        self.image = pygame.transform.scale(self.image, (self.TILE_SIZE,
                                                         self.TILE_SIZE))
        self.mask = pygame.mask.from_surface(self.image)
        self.isBroken = True

    def compare_rect_with_bot(self, rect: pygame.rect.Rect):
        if rect.x <= self.rect.x <= rect.x + rect.width\
                or rect.y <= self.rect.y <= rect.y + rect.width:
            return True
        return False

    def activate_bonus(self, name_bonus):
        if name_bonus == 'sh':
            for kx, ky in [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1],
                           [0, 1], [-1, 1], [-1, 0]]:
                x, y = self.rect.x + (kx * self.TILE_SIZE),\
                       self.rect.y + (ky * self.TILE_SIZE)
                empty_b = EmptyBot(x, y, self.TILE_SIZE, self.TILE_SIZE)
                c = pygame.sprite.spritecollideany(empty_b,
                                                   self.game.wall_group)
                if c and c.isBroken:
                    c.set_bonus(name_bonus)


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
        self.image = self.mask = self.id = None
        self.blink_img = pygame.transform.scale(load_image(
            f'{WORLDIMG_DIR}{self.type_wall[11]}'),
            (self.tile_size, self.tile_size))
        self.reload_mask(id)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.bonus_name = self.bonus_timer = self.bonus_delay = \
            self.blink_time = self.blink_timer = None

    def set_bonus(self, name_bonus):
        if name_bonus == 'sh':
            self.bonus_name = name_bonus
            self.bonus_timer = pygame.time.get_ticks()
            self.bonus_delay = 20000
            self.blink_time = self.bonus_delay * 1 / 5
            self.reload_mask(13)

    def reload_mask(self, set_id):
        self.id = set_id
        self.isBroken = True if self.id not in [2, 13] else False
        self.isWall = True if self.id not in [2] else False
        self.image = load_image(f'{WORLDIMG_DIR}{self.type_wall[self.id]}')
        self.image = pygame.transform.scale(self.image,
                                            (self.tile_size, self.tile_size))
        self.mask = pygame.mask.from_surface(self.image)

    def change_yourself(self, coords):
        x, y = coords
        max_s = self.tile_size              # 50
        half_s = max_s // 2 - max_s // 10 - 2  # 20
        half_s2 = half_s + max_s // 5 + 4      # 30
        if self.id == 11:
            if half_s <= x <= half_s2:
                if 0 <= y <= half_s:
                    self.reload_mask(7)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(10)
            elif 0 <= x <= half_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(9)
                elif 0 <= y <= half_s:
                    self.reload_mask(5)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(6)
            elif half_s2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(8)
                elif 0 <= y <= half_s:
                    self.reload_mask(3)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(4)
        elif self.id == 5:
            if half_s <= x <= half_s2:
                if half_s2 <= y <= max_s:
                    self.reload_mask(19)
            if max_s // 2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(18)
                elif 0 <= y <= half_s:
                    self.reload_mask(7)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(22)
            if 0 <= x <= max_s // 2 <= y <= max_s:
                self.reload_mask(9)
        elif self.id == 3:
            if half_s <= x <= half_s2 <= y <= max_s:
                self.reload_mask(21)
            if 0 <= x <= max_s // 2:
                if half_s <= y <= half_s2:
                    self.reload_mask(20)
                if 0 <= y <= half_s:
                    self.reload_mask(7)
                if half_s2 <= y <= max_s:
                    self.reload_mask(23)
            if max_s // 2 <= x <= max_s and max_s // 2 <= y <= max_s:
                self.reload_mask(8)
        elif self.id == 6:
            if half_s2 >= x >= half_s >= y >= 0:
                self.reload_mask(20)
            if half_s2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(21)
                elif 0 <= y <= half_s:
                    self.reload_mask(23)
            if 0 <= x <= half_s and 0 <= y <= max_s // 2:
                self.reload_mask(9)
            if max_s // 2 <= x <= max_s and max_s // 2 <= y <= max_s:
                self.reload_mask(10)
        elif self.id == 4:
            if half_s2 >= x >= half_s >= y >= 0:
                self.reload_mask(18)
            if 0 <= x <= max_s // 2 <= y <= max_s:
                self.reload_mask(10)
            if 0 <= x <= half_s:
                if half_s <= y <= max_s // 2:
                    self.reload_mask(19)
                elif 0 <= y <= half_s:
                    self.reload_mask(22)
            if max_s >= x >= max_s // 2 >= y >= 0:
                self.reload_mask(8)
        elif self.id == 10:
            if 0 <= y <= max_s // 2:
                if half_s <= x <= half_s2:
                    self.kill()
                elif 0 <= x <= half_s:
                    self.reload_mask(19)
                elif half_s2 <= x <= max_s:
                    self.reload_mask(21)
        elif self.id == 7:
            if max_s // 2 <= y <= max_s:
                if half_s <= x <= half_s2:
                    self.kill()
                elif 0 <= x <= half_s:
                    self.reload_mask(20)
                elif half_s2 <= x <= max_s:
                    self.reload_mask(18)
        elif self.id == 9:
            if max_s // 2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.kill()
                elif 0 <= y <= half_s:
                    self.reload_mask(20)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(19)
        elif self.id == 8:
            if 0 <= x <= max_s // 2:
                if half_s <= y <= half_s2:
                    self.kill()
                elif 0 <= y <= half_s:
                    self.reload_mask(18)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(21)
        elif self.id == 22:
            if 50 >= x >= 25 >= y >= 0:
                self.reload_mask(18)
            if 0 <= x <= 25 <= y <= 50:
                self.reload_mask(19)
        elif self.id == 23:
            if 50 >= x >= 25 and 25 <= y <= 50:
                self.reload_mask(21)
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.reload_mask(20)
        else:
            self.kill()

    def update(self, *args):
        if self.bonus_name is not None:
            now = pygame.time.get_ticks()
            if now - self.bonus_timer > self.bonus_delay:
                self.bonus_name = None
                self.reload_mask(11)
                return
            if now - self.bonus_timer > self.bonus_delay - self.blink_time:
                if self.blink_timer is None:
                    self.blink_timer = now - self.blink_time
                if now - self.blink_timer > 180:
                    img = self.image
                    self.image = self.blink_img
                    self.blink_img = img
                    self.blink_timer = now
                    return


class Bonus(pygame.sprite.Sprite):
    images = {
        's': 'star.png', 'c': 'clock.png', 'g': 'grenade.png',
        'h': 'helmet.png', 'p': 'pistol.png', 'sh': 'shovel.png',
        't': 'tank.png'
    }

    def __init__(self, game):
        super().__init__(game.all_sprites, game.bonus_group)
        available_bonuses = ['s', 's', 'g', 'g', 'c', 'h', 'p', 'sh', 't']
        self.game = game
        self.points = 500
        self.bonus = choice(available_bonuses)
        self.bonus = 'c'
        self.image = load_image(f"{DIR_FOR_TANKS_IMG}"
                                f"bonus\\{self.images[self.bonus]}")
        k = ((3 * self.game.TILE_SIZE) // 4) // self.image.get_rect().width
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_rect().width * k,
                                             self.image.get_rect().height * k))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.hide_image = pygame.Surface((self.rect.width, self.rect.height),
                                         pygame.SRCALPHA, 32)
        self.rect.center = [randrange(self.game.MAP_SIZE[0] +
                                      self.game.TILE_SIZE * 2,
                                      self.game.MAP_SIZE[2] -
                                      self.game.TILE_SIZE * 2),
                            randrange(self.game.MAP_SIZE[1] +
                                      self.game.TILE_SIZE * 2,
                                      self.game.MAP_SIZE[3] -
                                      self.game.TILE_SIZE * 2)]

        self.hide_timer = pygame.time.get_ticks()
        self.spawn_timer = pygame.time.get_ticks()
        self.spawn_delay = 10000
        self.blink_time = 2000

    def update(self, *args):
        now = pygame.time.get_ticks()
        if now - self.spawn_timer > self.spawn_delay:
            self.kill()
        if now - self.spawn_timer > self.spawn_delay - self.blink_time:
            if now - self.hide_timer > 180:
                img = self.image
                self.image = self.hide_image
                self.hide_image = img
                self.hide_timer = now
                return

    def activate_bonus(self, player):
        if self.bonus in ['t', 's', 'h', 'p']:
            player.activate_bonus(self.bonus)
        elif self.bonus in ['c', 'g']:
            self.game.bot_manager.activate_bonus(self.bonus)
        elif self.bonus in ['sh']:
            self.game.eagle.activate_bonus(self.bonus)
        self.kill()


class Shield(pygame.sprite.Sprite):
    shield_anim = {0: 's1.png', 1: 's2.png'}

    def __init__(self, player):
        super().__init__(player.game.all_sprites, player.game.animation_sprite)
        self.player = player
        self.shield_n = 0
        self.shield_timer = None
        self.last_update = pygame.time.get_ticks()
        self.shield_duration = 6000
        self.frame_rate = 50
        self.rect = self.player.rect.copy()
        self.image = pygame.Surface((self.rect.width, self.rect.height),
                                    pygame.SRCALPHA, 32)
        self.offset = 3

    def load_image(self):
        self.shield_n = 0 if self.shield_n == 1 else 1
        shield_image = load_image(
            f'{DIR_FOR_TANKS_IMG}\\'
            f'anim\\shield_anim\\'
            f'{self.shield_anim[self.shield_n]}')
        self.image = pygame.transform.scale(
            shield_image, (self.rect.width + self.offset * 2,
                           self.rect.height + self.offset * 2))
        self.rect = self.player.rect.copy()
        self.rect.x -= self.offset
        self.rect.y -= self.offset

    def update(self, *args):
        if not self.player.hidden:
            now = pygame.time.get_ticks()
            self.shield_timer = now if self.shield_timer is None\
                else self.shield_timer
            if now - self.shield_timer > self.shield_duration:
                self.player.with_shield = False
                self.kill()
            else:
                if now - self.last_update > self.frame_rate:
                    self.last_update = now
                    self.load_image()


class SpawnAnim(pygame.sprite.Sprite):
    anim_img = {0: 'b1.png', 1: 'b2.png', 2: 'b3.png', 3: 'b4.png'}

    def __init__(self, tank):
        super().__init__(tank.game.all_sprites, tank.game.animation_sprite)
        self.tank = tank
        self.anim_n = 0
        self.timer = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()
        self.duration = 1300
        self.frame_rate = 50
        self.rect = self.tank.rect.copy()
        self.image = None
        self.k = 1
        self.load_image()

    def load_image(self):
        self.anim_n += self.k
        if self.anim_n <= 0 or self.anim_n >= 3:
            self.k *= -1
        image = load_image(
            f'{DIR_FOR_TANKS_IMG}\\'
            f'anim\\spawn\\'
            f'{self.anim_img[self.anim_n]}')
        self.image = pygame.transform.scale(
            image, (self.rect.width, self.rect.height))
        self.rect = self.tank.rect.copy()
        self.rect.center = self.tank.rect.center

    def update(self, *args):
        now = pygame.time.get_ticks()
        if now - self.timer > self.duration:
            self.tank.hidden = False
            self.kill()
        else:
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.load_image()


class Explosion(pygame.sprite.Sprite):
    explosion = {0: 'b1.png', 1: 'b2.png', 2: 'b3.png',
                 3: 'b4.png', 4: 'b5.png'}

    def __init__(self, obj):
        super().__init__(obj.game.all_sprites, obj.game.animation_sprite)
        self.obj = obj
        self.type_obj = obj.__class__.__name__
        self.max_index = 3 if self.type_obj == 'Bullet' else 4
        self.frame = 0
        self.timer = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.k = self.obj.game.TILE_SIZE * (1 / 45)
        self.rect = self.obj.rect.copy()
        self.image = None
        self.load_image()

    def load_image(self):
        image = load_image(
            f'{DIR_FOR_TANKS_IMG}\\'
            f'anim\\anim_\\'
            f'{self.explosion[self.frame]}')
        rect = image.get_rect()
        image = pygame.transform.scale(
            image, (int(rect.width * self.k), int(rect.height * self.k)))
        image = pygame.transform.rotate(image,
                                        choice([10, 30, 45, 60, 180, 90]))
        self.image = image

    def update(self, *args):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            if self.frame == self.max_index:
                self.kill()
            else:
                center = self.rect.center
                self.load_image()
                self.rect = self.image.get_rect()
                self.rect.center = center
            self.frame += 1


class PointsAnim(pygame.sprite.Sprite):
    def __init__(self, game, summ_points, rect):
        super().__init__(game.all_sprites, game.animation_sprite)
        font = pygame.font.Font(None, game.TILE_SIZE - game.TILE_SIZE // 4)
        self.image = font.render(f"{summ_points}", True, pygame.Color('white'))
        self.rect = self.image.get_rect()

        self.rect.x = rect.centerx - self.rect.width // 2
        self.rect.y = rect.centery - self.rect.height // 2

        self.start_timer = pygame.time.get_ticks()
        self.duration = 500

    def update(self, *args, **kwargs):
        now = pygame.time.get_ticks()
        if now - self.start_timer > self.duration:
            self.image.set_alpha(max(0, self.image.get_alpha() - 10))
