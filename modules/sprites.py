import pygame
from settings import *
from random import random
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
        super().__init__()
        self.game = game
        self.type_tanks = 't1'
        self.player = player
        self.side = 't'
        self.move_trigger = False

        self.TILE_SIZE = tile_size
        self.image = None
        self.mask = None
        self.load_tanks_image()

        self.coords = coords
        self.rect = self.image.get_rect()
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

        self.speed = 2
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.bullet = None

        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()

    def set_properties(self):
        if self.type_tanks == 't1':
            self.speed = 1
        elif self.type_tanks == 't2':
            self.speed = 3
        elif self.type_tanks == 't3':
            self.shoot_delay = 100
        elif self.type_tanks == 't4':
            self.lives = 4

    def load_tanks_image(self):
        self.move_trigger = not self.move_trigger
        image = load_image(f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{self.images[f"{self.player}_{self.side}{int(self.move_trigger)}"]}'
                           if self.player == 1 else
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
        # self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def move_collide(self, side: str, speed=(0, 0)):
        self.side = side
        self.load_tanks_image()
        self.rect = self.rect.move(speed[0], speed[1])
        c = pygame.sprite.spritecollide(self, self.game.all_sprites, False,
                                        pygame.sprite.collide_mask)
        del c[c.index(self)]
        if self.game.eagle in c:
            del c[c.index(self.game.eagle)]
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
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
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
                bullet = Bullet(self.rect, self.side, self.game, self)
                bullet.add(self.game.all_sprites, self.game.bullets)
                self.bullet = bullet

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
                # TODO сделать уменьшение жизни у игрока и анимацию попадания
                self.kill()
            if c in self.game.bullets and c is not self:
                if self.who_shoot.__class__ != c.who_shoot.__class__:
                    self.kill()
                    c.kill()
            if c in self.game.mobs_group and \
                    self.who_shoot.__class__ == Player:
                c.kill()
                self.kill()
            if c == self.game.eagle:
                c.eagle_break()
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
    }

    def __init__(self, game, coords, tile_size, type_bot: str, number_tank):
        super().__init__(game.mobs_group, game.all_sprites)

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

        self.TILE_SIZE = tile_size
        self.image = self.mask = None
        self.load_tanks_image()

        self.coords = coords
        self.rect = self.image.get_rect()
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

        self.speed = 1
        self.speedx = 0
        self.speedy = 0
        self.lives = 1
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

        self.bullet = None
        self.bullet_speed = 5
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()

        self.start_time = pygame.time.get_ticks()
        self.change_side_timer = 2000

        self.target = None

        self.set_properties()

    def update(self, *event):
        self.move()
        self.shoot()

    def kill(self):
        if self.lives > 1:
            self.lives -= 1
            # TODO при уменьшении жизней у бота (самый крупный)
            #  необходимо изменить его внешний вид
            return
        super().kill()

    def set_properties(self):
        if self.number in [4, 11, 18]:
            self.is_bonus = True
        if self.type_tanks == 't1':
            self.speed = 1
        elif self.type_tanks == 't2':
            self.speed = 3
        elif self.type_tanks == 't3':
            self.shoot_delay = 100
        elif self.type_tanks == 't4':
            self.lives = 4

    def setTarget(self, target):
        self.target = target

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        # self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def load_tanks_image(self):
        self.move_trigger = not self.move_trigger
        if self.is_bonus:
            self.bonus_trigger = not self.bonus_trigger
        now = pygame.time.get_ticks()
        req = f"{self.side}{int(self.move_trigger)}"
        """Если у нас танк является бонусным, то он должен мигать"""
        if now - self.bonus_trigger_timer > self.bonus_trigger_delay and\
                self.is_bonus:
            if now - self.bonus_trigger_timer > self.bonus_trigger_delay * 2:
                self.bonus_trigger_timer = now
            req = f"{self.side}{int(self.move_trigger)}" \
                f"{int(self.move_trigger)}"
        name_image = self.images[req]
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
        c = pygame.sprite.spritecollide(self, self.game.all_sprites, False,
                                        pygame.sprite.collide_mask)
        del c[c.index(self)]
        if self.game.eagle in c:
            del c[c.index(self.game.eagle)]
        if c or self.game.map.check_collide(self.rect):
            self.rect = self.rect.move(-speed[0], -speed[1])
            if self.target is None:
                self.change_side()
            if self.target is not None:
                return False, None if not c else c[0]

    def get_nearest_players_pos(self):
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
        if pygame.sprite.spritecollide(empty_b, self.game.wall_group, False,
                                       pygame.sprite.collide_mask):
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
                return
            rez = self.check_side(pref_side)
            if rez:
                self.side = pref_side
            print(self.side, self.prev_side,
                  pref_side, '-', self.sides_flags,
                  (self.is_stop_x, self.is_stop_y))
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
            players_rect = self.get_nearest_players_pos()
            go_to(players_rect)

        if self.target == 'eagle':
            rect = self.game.eagle.rect
            go_to(rect)

    def shoot(self, custom=False):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.bullet is None or not self.bullet.alive():
                if random() < 1 / 10 or self.compare_rect() or custom:
                    bullet = Bullet(self.rect, self.side, self.game, self)
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
        if (p_x == b_x and b_y == p_y) or \
            (players_rect.left == self.rect.right and
                (players_rect.top == self.rect.top or
                    players_rect.bottom == self.rect.bottom)) or\
            (players_rect.right == self.rect.left and
                (players_rect.top == self.rect.top or
                    players_rect.bottom == self.rect.bottom)) or \
            (players_rect.top == self.rect.bottom and
                (players_rect.left == self.rect.left or
                    players_rect.right == self.rect.right)) or \
            (players_rect.bottom == self.rect.top and
                (players_rect.left == self.rect.left or
                    players_rect.right == self.rect.right)):
            self.is_stop_y = False
            self.is_stop_x = False
            return None
        if p_y >= b_y and not self.is_stop_y:
            if not (p_y - self.speed <= b_y <= p_y + self.speed):
                return 'b'
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
        super().__init__(game.all_sprites)
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
        self.reload_mask(id)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def reload_mask(self, set_id):
        self.id = set_id
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
