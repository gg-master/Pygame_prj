# Игра Shmup - 1 часть
# Cпрайт игрока и управление
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# 8-Bit Universe – Smells Like Teen Spirit
# from https://x-minusovka.ru/?song=8-Bit+Universe+
# %E2%80%93+Smells+Like+Teen+Spirit
import pygame
import random
from os import path

#  Загрузка изображений # В кавычках нужно указать путь к папке с файлами
img_dir = path.join(path.dirname(__file__),
                    'E:/Game on Python/SpaceShooterRedux')
snd_dir = path.join(path.dirname(__file__),
                    'E:/Game on Python/SpaceShooterRedux/sounds')

WIDTH = 600  # 480
HEIGHT = 850  # 600
FPS = 60
# settings
POWER_TIME = 5000

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

# Загрузка музыки
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'sfx_shieldDown.ogg'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'sfx_shieldUp.ogg'))

shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))

expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
expl_sounds_big = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))

# pygame.mixer.music.load(path.join(snd_dir,
#                                   'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.load(path.join(snd_dir,
                                  'Smells Like Teen.mp3'))
pygame.mixer.music.set_volume(0.4)

# Загрузка всей игровой графики
powerup_images = dict()
powerup_images['shield'] = \
    pygame.image.load(path.join(img_dir,
                                'E:/Game on Python/SpaceShooterRedux'
                                '/PNG/Power-ups/shield_gold.png')).convert()
powerup_images['gun'] = \
    pygame.image.load(path.join(img_dir, 'E:/Game on Python/'
                                         'SpaceShooterRedux/PNG/'
                                         'Power-ups/bolt_gold.png')).convert()

background = \
    pygame.image.load(path.join(img_dir,
                                'Backgrounds/darkPurple.png')).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))

player_img = pygame.image.load(path.join(img_dir,
                                         "PNG/playerShip1_red.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (35, 29))
player_mini_img.set_colorkey(BLACK)
# pictures for meteors
meteor_list = []
for m_i in ["PNG/Meteors/meteorBrown_med1.png",
            "PNG/Meteors/meteorBrown_big1.png",
            "PNG/Meteors/meteorGrey_med1.png"]:
    meteor_list.append(pygame.image.load(path.join(img_dir, m_i)).convert())

# pictures for bullet
bullet_img = \
    pygame.image.load(path.join(img_dir,
                                "PNG/Lasers/laserRed16.png")).convert()
explosion_anim = dict()
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = \
        'E:/Game on Python/SpaceShooterRedux/bombs' \
        '/regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'E:/Game on Python/SpaceShooterRedux/' \
               'player_bombs/sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 35
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def update(self):
        # показать, если скрыто
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -10
        if keystate[pygame.K_RIGHT]:
            self.speedx = 10
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if keystate[pygame.K_SPACE]:
            self.shoot()
        if self.power >= 2 and pygame.time.get_ticks() - \
                self.power_time > POWER_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play().set_volume(0.5)
            elif self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play().set_volume(0.5)

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_list)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        # self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or \
                self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # удалить спрайт, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # удалить спрайт, если он заходит за верхнюю часть экрана
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


font_name = pygame.font.match_font('arial')


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 40 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, 'SHUMP', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, 'Press a key to begin', 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Цикл игры
game_over = True
running = True
pygame.mixer.music.play(loops=-1)
while running:
    if game_over:
        show_go_screen()
        powerups = pygame.sprite.Group()
        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        score = 0
        for i in range(8):
            newmob()
        game_over = False
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == pygame.QUIT:
            running = False
    # Обновление
    all_sprites.update()

    # Проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, True,
                                       pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        random.choice(expl_sounds).play() if player.shield > 0 else ''
        if player.shield <= 0:
            if player.lives <= 0:
                player.kill()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            expl_sounds_big.play()
            player.hide()
            player.lives -= 1
            player.shield = 100

    # Если игрок умер, игра окончена
    if not player.alive() and not death_explosion.alive():
        game_over = True
    # Проверка, попала ли пуля игрока в моба
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play().set_volume(0.5)
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    # Проверка столкновений игрока и улучшения
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            shield_sound.play()
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            power_sound.play()
            player.powerup()
    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_lives(screen, WIDTH - 120, 5, player.lives,
               player_mini_img)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()
