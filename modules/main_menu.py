import os
import pygame as pg
from client import Client, update_fps
from default_funcs import load_image
import sys
import time
import json

os.chdir(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
if os.getcwd().endswith('modules'):
    os.chdir('..')

FPS = 60
pg.init()
display_info = pg.display.Info()

# Задаём размеры экрана
WIDTH, HEIGHT = display_info.current_w, display_info.current_h
screen = pg.display.set_mode((WIDTH, HEIGHT))

background = pg.Surface((WIDTH, HEIGHT))
background.fill((0, 0, 0, 0))
pg.display.set_caption('Tanks Battle')
pg.display.set_icon(load_image('system_image/Tanks_Battle.png'))
clock = pg.time.Clock()
maps = ['']

# Загружаем музыку
pg.mixer.music.load('data/music/music/main_theme.wav')
click_sound = pg.mixer.Sound('data/sounds/click.wav')
with open('settings/settings.json') as f:
    data = json.load(f)
    music_v = data['player_settings']['music'] / 100
    sound_v = data['player_settings']['effects'] / 100
pg.mixer.music.set_volume(music_v)
click_sound.set_volume(sound_v)

# Настройка курсора мыши
pg.mouse.set_visible(False)
cursor = pg.image.load('data/system_image/cursor.png').convert_alpha()

# Подгруажем некоторые картинки
fon = pg.transform.scale(pg.image.load('data/system_image'
                                       '/main_menu_bckgrnd.'
                                       'png').convert_alpha(),
                         (WIDTH,
                          HEIGHT))
st_screen = pg.Surface(screen.get_size())
bg_screen = pg.Surface(screen.get_size())
bg_screen.blit(fon, (0, 0))
lvl_scr = pg.transform.scale(pg.image.load('data/system_image'
                                           '/main_menu_bckgrnd.png'),
                             (WIDTH, HEIGHT))
lvl_scrn = pg.Surface(screen.get_size())
lvl_scrn.blit(lvl_scr, (0, 0))
lvl_image = None
border = pg.transform.scale(pg.image.load('data/system_image/'
                                          'border.png'), (
                                round(WIDTH * 0.390625),
                                round(HEIGHT * 0.6944444)))
# Загружаем плашку "Tanks Battle"
tanks_battle = pg.image.load(
    'data/system_image/TanksBattle.png').convert_alpha()
tanks_battle_rect = tanks_battle.get_rect()

# Создаём темный фильтр
bck_dark = pg.Surface((WIDTH, HEIGHT))
bck_dark.fill((0, 0, 0))
bck_dark.set_alpha(100)

# Задаём стандартный тип игры и уровень
map_index = (1, 1)

# Задаём флаги для отображения окон
pause = False
exit_wnd_f = False
settings_wnd_f = False
rules_wnd_f = False
is_save = False
bck_is_drk = False
game_mode_f = False


def terminate():
    """Завершение работы программы"""
    pg.quit()
    sys.exit()


def change_exit_f():
    """Смена флага отображения меню выхода"""
    global exit_wnd_f
    exit_wnd_f = not exit_wnd_f
    change_pause()
    return [start_screen, (False,)]


def change_settings_f():
    """Смена флага отображения меню настроек"""
    global settings_wnd_f, setting_window, is_save
    settings_wnd_f = not settings_wnd_f
    # Задаём сохраненное значение грмкости музыки
    pg.mixer.music.set_volume(music_v)
    click_sound.set_volume(sound_v)
    if settings_wnd_f:
        setting_window.update()
    change_pause()
    return [start_screen, (False,)]


def default_settings():
    """Установка стандартных настроек"""
    global setting_window
    with open('settings/default_settings.json') as f:
        data = json.load(f)
        with open('settings/settings.json', 'w') as f1:
            json.dump(data, f1)
    setting_window.update()
    return [start_screen, (False,)]


def change_pause():
    """Смена флага паузы"""
    global pause
    pause = not pause


def change_lvl_image(index):
    """Изменение картинки уровня"""
    global lvl_image, map_index
    print(index, 'index')
    map_index = list(map(int, index.split('_')))
    print(map_index, 'ch')
    lvl_image = pg.transform.scale(
        pg.image.load(
            f'data/system_image/lvl_images/{index}.png').convert_alpha(),
        (round(WIDTH * 0.32447916), round(HEIGHT * 0.56296)))
    return [choose_level_screen, map_index]


def start_game():
    """старт игры"""
    running = True
    pg.mixer.music.stop()
    # Созаём клиент игры
    client = Client(map_index[0], map_index[1], screen)
    while running:
        # Цикл обработки событий
        screen.fill(pg.Color('black'))
        if client.is_exit:
            client.cursor.set_visible(False)
            pg.mouse.set_visible(True)
            return [play_music]
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            client.update(event)
        client.update()
        client.render()
        screen.blit(update_fps(clock), (10, 0))
        if pg.mouse.get_focused():
            client.cursor.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
    pg.quit()


class InputBox:
    """Класс поля ввода"""

    def __init__(self, x, y, w, h, text='', centering=False, usual=True,
                 btn=False):
        # Задаём актиынй и неактивный цвета поля ввода
        self.color_inactive = (55, 56, 56)
        self.color_active = (0, 0, 0)
        # Задаём прямоугольник поля ввода
        self.rect = pg.Rect(x, y, w, h)
        self.color = self.color_inactive
        self.text = text
        # Создаем шрифт и текст
        self.font = pg.font.Font(None, round(w * 0.2285714))
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.inactive_border = 2
        self.active_border = 3
        self.border = 2
        self.usual = usual
        # Устанавливаем флаг оцентровки текста
        self.centering = centering
        self.btn = btn

    def handle_event(self, event):
        """Проверка на событие"""
        # Обработка события
        if event.type == pg.MOUSEBUTTONDOWN:
            # Проверка на фхождение координат события в прямоугольник поля
            # ввода
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Меняем значение цвета в зависимости от статуса активности
            self.color = self.color_active if self.active \
                else self.color_inactive
            self.border = self.active_border if self.active \
                else self.inactive_border
        # Если поле необычное(задаёт имя кнопки), то очищаем поле
        if self.active and not self.usual:
            self.text = ''
        # Обрабатываем нажатую кнопку
        if event.type == pg.KEYDOWN:
            if self.active:
                # если поле обычное, то прибовлеям unicode кнопки
                if self.usual:
                    if event.key == pg.K_RETURN:
                        self.text = ''
                    elif event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode
                else:
                    # Задаём корректное отображение названия кнопки
                    self.text = pg.key.name(event.key)
                    self.text = f'keypad ' \
                                f'{self.text.split("[")[1].split("]")[0]}' \
                        if '[' in self.text or ']' in self.text else self.text
                    self.btn = event.key
                    self.active = False
        # Задаём ограничение на кол-во символов в строке
        self.text = self.text[:10]
        # Создаём текст
        self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        """Отрисовка блока"""
        # Проверка на режим отображения текста
        if not self.centering:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        else:
            screen.blit(self.txt_surface, (
                self.rect.x + (self.rect.w - self.txt_surface.get_width()) / 2,
                self.rect.y + 5))
        # Отрисовываем границу поля ввода
        pg.draw.rect(screen, self.color, self.rect, self.border)


class SliderBar:
    """Микшер громкости"""

    def __init__(self, x, y, width, height, orientation, value=100, music=0):
        self.x, self.y = x, y
        # В зависимости от ориентации задаём размеры блока
        self.width, self.height = (width, height) if orientation else (
            height, width)
        # Созаём штангу микшера
        self.post = pg.Surface(
            (self.width / 3, self.height + self.height / 25))
        # Создаём ползунок
        self.slider = pg.Surface((self.width, self.height / 25))
        # Задаём цвета
        self.post.fill((47, 48, 48))
        self.slider.fill((84, 87, 87))
        # Загружаем прозрачный фон для блока
        self.bar = pg.transform.scale(pg.image.load('data/system_image/'
                                                    'alpha_0.'
                                                    'png').convert_alpha(),
                                      (
                                          self.width,
                                          int(self.height + self.height / 25)))
        self.bar.blit(self.post, (self.width / 3, 0))
        # Задаём значение pxperv(pixels per value), то есть сколько пикселей
        # приходится на 1 значение громкости
        self.pxperv = self.height / 100
        self.value = value
        self.music = music

    def draw(self):
        """Отрисовка слайдербара"""
        returning = self.bar.copy()
        returning.blit(self.slider,
                       (0, self.height - self.value * self.pxperv))
        return returning

    def click(self, pos):
        """Изменение значения слайдебара"""
        x, y = pos
        if self.x - 10 <= x <= self.x + self.width + 10 and \
                self.y <= y <= self.y + self.height:
            self.value = 100 - (y - self.y) / self.pxperv
            # В зависимости от значения меняю громкость музыки/эффектов
            if not self.music:
                pg.mixer.music.set_volume(self.value / 100)
            elif self.music == 1:
                click_sound.set_volume(self.value / 100)


class SettingsWindow:
    """Меню настроек"""

    def __init__(self):
        self.width, self.height = WIDTH // 3, round(HEIGHT * 0.4)
        self.background = pg.transform.scale(
            pg.image.load('data/system_image/'
                          'settings_wnd_bckgrnd.jpg').convert_alpha(),
            (self.width, self.height))
        # Созаём верхнюю плашку окна
        self.top = pg.Surface((self.width, self.height / 8))
        self.top.fill((70, 70, 68))
        self.window_scr = pg.Surface((self.width, self.height))
        # Флаги на корректность введённых данных
        self.none_button = False
        self.same_button = False
        # Создаём статичный задник
        self.create_background()

    def create_background(self):
        """Создание статичных элементов окна"""
        # Создаём шрифты
        font_head = pg.font.SysFont("comicsans", round(0.059375 * self.width))
        font = pg.font.SysFont("comicsans", round(0.0421875 * self.width))
        font_little_head = pg.font.SysFont("comicsans",
                                           round(0.046875 * self.width))
        font_little = pg.font.SysFont("comicsans",
                                      round(0.0390625 * self.width))
        # Создаём текст
        header_text = font_head.render('Настройки', True, (255, 255, 255))
        music_text = font.render('Музыка', True, (0, 0, 0))
        eff_text = font.render('Эффекты', True, (0, 0, 0))
        player_nick_text = font.render('Ник игрока', True, (0, 0, 0))
        forward_text = font.render('Вперёд', True, (0, 0, 0))
        back_text = font.render('Назад', True, (0, 0, 0))
        left_text = font.render('Влево', True, (0, 0, 0))
        right_text = font.render('Вправо', True, (0, 0, 0))
        shoot_text = font.render('Выстрел', True, (0, 0, 0))
        control_text = font_little_head.render('Управление', True, (0, 0, 0))
        self.text_length_message1 = font_little.render(
            'Длина ника игрока не может', True, (0, 0, 0))
        self.text_length_message2 = font_little.render('превышать 8 символов',
                                                       True, (0, 0, 0))
        self.none_button_text1 = font_little.render('Вы не назначили', True,
                                                    (0, 0, 0))
        self.none_button_text2 = font_little.render('одну из кнопок', True,
                                                    (0, 0, 0))
        self.same_buttons_text = font_little.render('Кнопки совпадают', True,
                                                    (0, 0, 0))
        # Наносим верхнюю плашку
        self.background.blit(self.top, (0, 0))
        # Наноис текст
        self.background.blit(music_text, (
            WIDTH * 0.03125 - music_text.get_width() / 2, HEIGHT * 0.32407407))
        self.background.blit(eff_text, (
            WIDTH * 0.083333 - eff_text.get_width() / 2, HEIGHT * 0.32407407))
        self.background.blit(control_text, (
            WIDTH * 0.20833 - control_text.get_width() / 2,
            HEIGHT * 0.125 - int(control_text.get_height() / 2)))
        self.background.blit(player_nick_text, (WIDTH * 0.114583,
                                                HEIGHT * 0.0805 - int(
                                                    player_nick_text.
                                                    get_height() / 2)))
        self.background.blit(forward_text, (WIDTH * 0.114583,
                                            HEIGHT * 0.162037 - int(
                                                player_nick_text.
                                                get_height() / 2)))
        self.background.blit(back_text, (WIDTH * 0.114583,
                                         HEIGHT * 0.2037 - int(
                                             player_nick_text.
                                             get_height() / 2)))
        self.background.blit(left_text, (WIDTH * 0.114583,
                                         HEIGHT * 0.24537 - int(
                                             player_nick_text.
                                             get_height() / 2)))
        self.background.blit(right_text, (WIDTH * 0.114583,
                                          HEIGHT * 0.287037 - int(
                                              player_nick_text.
                                              get_height() / 2)))
        self.background.blit(shoot_text, (WIDTH * 0.114583,
                                          HEIGHT * 0.3287037 - int(
                                              player_nick_text.
                                              get_height() / 2)))
        self.background.blit(header_text, (
            (self.width - header_text.get_width()) / 2, self.height * 0.03))
        # Наносим границы
        pg.draw.line(self.background, (57, 59, 61), (0, self.height * 0.11805),
                     (self.width, self.height * 0.11805), 3)
        pg.draw.rect(self.background, (47, 48, 48), (round(self.width *
                                                           0.015625),
                                                     round(self.height *
                                                           0.13953488372),
                                                     round(self.width *
                                                           0.96875),
                                                     round(self.height *
                                                           0.756944)), 2)
        pg.draw.rect(self.background, (57, 59, 61),
                     (0, 0, self.width, self.height), 6)
        pg.draw.line(self.background, (47, 48, 48),
                     (self.width * 0.171875, round(self.height * 0.13888)),
                     (self.width * 0.171875, self.height * 0.8912037), 2)
        pg.draw.line(self.background, (47, 48, 48),
                     (self.width * 0.328125, round(self.height * 0.13888)),
                     (self.width * 0.328125, self.height * 0.8912037), 2)
        pg.draw.line(self.background, (47, 48, 48),
                     (self.width * 0.328125, self.height * 0.2662037),
                     (self.width * 0.984375, self.height * 0.2662037), 2)

    def draw(self, win):
        """Отрисовка меню настроек"""
        self.window_scr.blit(self.background, (0, 0))
        if self.none_button:
            self.window_scr.blit(self.none_button_text1, (
                self.width * 0.0234375, self.height * 0.90277777))
            self.window_scr.blit(self.none_button_text2, (
                self.width * 0.0234375, self.height * 0.949074))
        elif self.same_button:
            self.window_scr.blit(self.same_buttons_text, (
                self.width * 0.0234375, self.height * 0.90277777))
        self.window_scr.blit(self.music_bar.draw(),
                             (self.width * 0.078125, self.height * 0.162037))
        self.window_scr.blit(self.effects_bar.draw(),
                             (self.width * 0.234375, self.height * 0.162037))
        win.blit(self.window_scr,
                 ((WIDTH - self.width) / 2, (HEIGHT - self.height) / 1.883720))

    def update(self):
        """Обновление значений полей"""
        self.none_button = False
        self.same_button = False
        # Из Json файла получаем настройки игры
        with open('settings/settings.json') as file:
            data = json.load(file)
            self.first_player_nick = data["player_settings"][
                "first_player_nick"]
            self.second_player_nick = data["player_settings"][
                "second_player_nick"]
            self.forward_btn_1 = data["player_settings"]["forward_move_btn_1"]
            self.forward_btn_1_text = data["player_settings"][
                "forward_move_btn_1"]
            self.back_btn_1 = data["player_settings"]["back_move_btn_1"]
            self.back_btn_1_text = data["player_settings"]["back_move_btn_1"]
            self.left_btn_1 = data["player_settings"]["left_move_btn_1"]
            self.left_btn_1_text = data["player_settings"]["left_move_btn_1"]
            self.right_btn_1 = data["player_settings"]["right_move_btn_1"]
            self.right_btn_1_text = data["player_settings"]["right_move_btn_1"]
            self.shoot_btn_1 = data["player_settings"]["shoot_btn_1"]
            self.shoot_btn_1_text = data["player_settings"]["shoot_btn_1"]
            self.forward_btn_2 = data["player_settings"]["forward_move_btn_2"]
            self.forward_btn_2_text = data["player_settings"][
                "forward_move_btn_2"]
            self.back_btn_2 = data["player_settings"]["back_move_btn_2"]
            self.back_btn_2_text = data["player_settings"]["back_move_btn_2"]
            self.left_btn_2 = data["player_settings"]["left_move_btn_2"]
            self.left_btn_2_text = data["player_settings"]["left_move_btn_2"]
            self.right_btn_2 = data["player_settings"]["right_move_btn_2"]
            self.right_btn_2_text = data["player_settings"]["right_move_btn_2"]
            self.shoot_btn_2 = data["player_settings"]["shoot_btn_2"]
            self.shoot_btn_2_text = data["player_settings"]["shoot_btn_2"]
            self.music_bar = SliderBar(round(WIDTH * 0.359375),
                                       round(HEIGHT * 0.388888),
                                       round(WIDTH * 0.0078125),
                                       round(HEIGHT * 0.23148), True,
                                       value=data["player_settings"]["music"])
            self.effects_bar = SliderBar(round(WIDTH * 0.41145833),
                                         round(HEIGHT * 0.388888),
                                         round(WIDTH * 0.0078125),
                                         round(HEIGHT * 0.23148), True,
                                         value=data["player_settings"][
                                             "effects"], music=1)
        # Установка значений микшеров громкости
        pg.mixer.music.set_volume(data["player_settings"]["music"] / 100)
        click_sound.set_volume(data["player_settings"]["effects"] / 100)
        # Установка значений полей ввода
        self.line_edits_arr = [
            InputBox(WIDTH * 0.5052083, HEIGHT * 0.386111, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.first_player_nick,
                     centering=True),
            InputBox(WIDTH * 0.5833333, HEIGHT * 0.386111, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.second_player_nick,
                     centering=True),
            InputBox(WIDTH * 0.5052083, HEIGHT * 0.467592, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.forward_btn_1_text,
                     centering=True, usual=False, btn=self.forward_btn_1),
            InputBox(WIDTH * 0.5833333, HEIGHT * 0.467592, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.forward_btn_2_text,
                     centering=True, usual=False, btn=self.forward_btn_2),
            InputBox(WIDTH * 0.5052083, HEIGHT * 0.50925925, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.back_btn_1_text,
                     centering=True, usual=False, btn=self.back_btn_1),
            InputBox(WIDTH * 0.5833333, HEIGHT * 0.50925925, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.back_btn_2_text,
                     centering=True, usual=False, btn=self.back_btn_2),
            InputBox(WIDTH * 0.5052083, HEIGHT * 0.550925, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.left_btn_1_text,
                     centering=True, usual=False, btn=self.left_btn_1),
            InputBox(WIDTH * 0.5833333, HEIGHT * 0.550925, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.left_btn_2_text,
                     centering=True, usual=False, btn=self.left_btn_2),
            InputBox(WIDTH * 0.5052083, HEIGHT * 0.5925925, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.right_btn_1_text,
                     centering=True, usual=False, btn=self.right_btn_1),
            InputBox(WIDTH * 0.5833333, HEIGHT * 0.5925925, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.right_btn_2_text,
                     centering=True, usual=False, btn=self.right_btn_2),
            InputBox(WIDTH * 0.5052083, HEIGHT * 0.634259, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.shoot_btn_1_text,
                     centering=True, usual=False, btn=self.shoot_btn_1),
            InputBox(WIDTH * 0.5833333, HEIGHT * 0.634259, WIDTH * 0.0729166,
                     HEIGHT * 0.0277777, text=self.shoot_btn_2_text,
                     centering=True, usual=False, btn=self.shoot_btn_2)]

    def saving(self):
        """Сохранение значений полей"""
        global is_save, music_v, sound_v
        is_save = True
        # Проверка на пустые поля
        if any([not x.text for x in self.line_edits_arr]):
            self.none_button = True
            return [start_screen, (False,)]
        # Проверка на одинаковые поля
        if len(set([x.text for x in self.line_edits_arr])) != len(
                [x.text for x in self.line_edits_arr]):
            self.same_button = True
            return [start_screen, (False,)]
        # Запись настроек в Json файл
        with open('settings/settings.json') as f:
            data = json.load(f)
        data['player_settings']['music'] = self.music_bar.value
        data['player_settings']['effects'] = self.effects_bar.value
        data['player_settings']['first_player_nick'] = self.line_edits_arr[
            0].text
        data['player_settings']['second_player_nick'] = self.line_edits_arr[
            1].text
        data['player_settings']['forward_move_btn_1'] = self.line_edits_arr[
            2].text
        data['player_settings']['forward_move_btn_2'] = self.line_edits_arr[
            3].text
        data['player_settings']['back_move_btn_1'] = self.line_edits_arr[
            4].text
        data['player_settings']['back_move_btn_2'] = self.line_edits_arr[
            5].text
        data['player_settings']['left_move_btn_1'] = self.line_edits_arr[
            6].text
        data['player_settings']['left_move_btn_2'] = self.line_edits_arr[
            7].text
        data['player_settings']['right_move_btn_1'] = self.line_edits_arr[
            8].text
        data['player_settings']['right_move_btn_2'] = self.line_edits_arr[
            9].text
        data['player_settings']['shoot_btn_1'] = self.line_edits_arr[10].text
        data['player_settings']['shoot_btn_2'] = self.line_edits_arr[11].text
        music_v, sound_v = (self.music_bar.value / 100,
                            self.effects_bar.value / 100)
        # Установка новых значений микшероов громкости
        pg.mixer.music.set_volume(music_v)
        click_sound.set_volume(sound_v)
        with open('settings/settings.json', 'w') as f:
            json.dump(data, f)
        self.update()
        return [start_screen, (False,)]


class ConfirmWindow:
    """Окно подтверждения"""

    def __init__(self, header_text, confirm_text):
        self.header_text = header_text
        self.confirm_text = confirm_text
        self.width, self.height = int(0.187 * WIDTH), int(0.15 * HEIGHT)
        self.background = pg.Surface((self.width, self.height))
        # Созаём верхнюю плашку окна
        self.top = pg.Surface((self.width, self.height / 6))
        self.top.fill((70, 70, 68))
        self.background.fill((147, 145, 142))
        self.window_scr = pg.Surface((self.width, self.height))

    def draw(self, win):
        """Отрисвка окна"""
        # Создаём шрифты
        font_head = pg.font.SysFont("comicsans", round(0.015625 * WIDTH))
        font_conf = pg.font.SysFont("comicsans", round(0.013 * WIDTH))
        # Создаём текст
        header_text = font_head.render(self.header_text, True, (255, 255, 255))
        confirm_text = font_conf.render(self.confirm_text, True, (15, 15, 14))
        # Наносим на экран задник и верхнюю плашку
        self.window_scr.blit(self.background, (0, 0))
        self.window_scr.blit(self.top, (0, 0))
        # Наносим текст
        self.window_scr.blit(header_text, (
            (self.width - header_text.get_width()) / 2, self.height * 0.03))
        self.window_scr.blit(confirm_text, (
            (self.width - confirm_text.get_width()) / 2, self.height / 4.5))
        # Отрисовка границ
        pg.draw.line(self.window_scr, (57, 59, 61), (0, self.height * 0.16),
                     (self.width, self.height * 0.16), 3)
        pg.draw.rect(self.window_scr, (57, 59, 61),
                     (0, 0, self.width, self.height), 6)
        win.blit(self.window_scr,
                 ((WIDTH - self.width) / 2 + 2, (HEIGHT - self.height) / 2))


class Button:
    """Класс кнопки"""

    def __init__(self, text, x, y, width=round(WIDTH * 0.32083),
                 height=round(HEIGHT * 0.0629629), size=round(WIDTH * 0.02083),
                 limit=(0, 0)):
        self.x = x
        self.y = y
        # Задаём значение урезания радиуса действия кнопки
        self.limit_x = limit[0]
        self.limit_y = limit[1]
        # Размер шрифта
        self.size = size
        # Загружаем изображение обыной кнопки и нажатой
        self.normal_image = pg.transform.scale(
            pg.image.load('data/system_image/'
                          'button_normal.png').convert_alpha(),
            (width, height))
        self.hover_image = pg.transform.scale(
            pg.image.load('data/system_image/'
                          'button_hovered.png').convert_alpha(),
            (width, height))
        # Зададём размеры кнопки
        self.width, self.height = width, height
        # Создаем шрифт
        font = pg.font.SysFont("comicsans", self.size)
        # Создаём текст кнопки
        self.text = font.render(text, True, (255, 255, 255))

    def draw(self, win, flag=True):
        """Отрисовка кнопки"""
        # Получаем координаты мыши
        x1, y1 = pg.mouse.get_pos()
        # если координаты мыши входит в границы кнопки, то меняем изображение
        # кнопки на новое, иначе ставим обычное
        if flag and self.x + self.limit_x <= x1 <= self.x + self.width - \
                self.limit_x and self.y <= y1 <= self.y + self.height:
            win.blit(self.hover_image, (self.x, self.y))
            win.blit(self.text,
                     (self.x + self.width / 2 - self.text.get_width() / 2,
                      self.y + self.height / 2 - self.text.get_height() /
                      1.65))
        else:
            win.blit(self.normal_image, (self.x, self.y))
            win.blit(self.text,
                     (self.x + self.width / 2 - self.text.get_width() / 2,
                      self.y + self.height / 2 - self.text.get_height() / 1.9))

    def click(self, pos, action, *args):
        """Активация кнопки"""
        # Получаем кординаты нажатия
        x1, y1 = pos[0], pos[1]
        # Если координаты нажатия вхоядт в границы кнопки, то вызываем функцию
        # кнопки
        if (self.x + self.limit_x <= x1 <= self.x + self.width - self.limit_x
                and self.y <= y1 <= self.y + self.height and action):
            click_sound.play()
            # Проерка на наличие аргрументов функции
            if args[0][0]:
                return [action, args[0][0]]
            else:
                return [action]
        else:
            return []


def choose_level_screen(typ):
    """Меню выбора уровня"""
    global lvl_image, map_index, game_mode_f
    # Проерка на первое открытие окна
    print(typ)
    if not game_mode_f:
        game_mode_f = True
        # Подграем нужную картинку в зависимости от типа игры
        if ((type(typ) == tuple or type(typ) == list) and typ[0] == 1) or typ == 1:
            lvl_image = pg.transform.scale(pg.image.load('data'
                                                         '/system_image'
                                                         '/lvl_images/1_1.p'
                                                         'ng').convert_alpha(),
                                           (round(WIDTH * 0.32447916),
                                            round(HEIGHT * 0.56296)))
            map_index = (1, 1)
        else:
            lvl_image = pg.transform.scale(pg.image.load('data'
                                                         '/system_image'
                                                         '/lvl_images/2_1.p'
                                                         'ng').convert_alpha(),
                                           (round(WIDTH * 0.32447916),
                                            round(HEIGHT * 0.56296)))
            map_index = (2, 1)
    print(map_index, 'mi')
    run = True
    # Цикл обработки событий
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Вызываем кнопки в зависимости т типа игры
                if ((type(typ) == tuple or type(typ) == list) and typ[0] == 1) or typ == 1:
                    response = [btn.click(event.pos, act, arg)
                                for btn, act, arg in lvl_scrn_buttons_1]
                else:
                    response = [btn.click(event.pos, act, arg)
                                for btn, act, arg in lvl_scrn_buttons_2]
                for x in response:
                    if len(x):
                        return x
                pg.time.delay(1)
        # Отрисовка меню выбора уровня
        st_screen.fill((0, 0, 0))
        st_screen.blit(bg_screen, (0, 0))
        if typ:
            [i[0].draw(st_screen) for i in lvl_scrn_buttons_1]
        else:
            [i[0].draw(st_screen) for i in lvl_scrn_buttons_2]
        st_screen.blit(lvl_image, (WIDTH * 0.60677083, HEIGHT * 0.1185))
        st_screen.blit(border, (WIDTH * 0.57291666, HEIGHT * 0.05))
        pg.draw.rect(st_screen, (57, 59, 61), (round(WIDTH * 0.57291666),
                                               round(HEIGHT * 0.05),
                                               round(WIDTH * 0.390625),
                                               round(HEIGHT * 0.6944444)), 6)
        st_screen.blit(cursor, pg.mouse.get_pos())
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def game_mode_screen():
    """Меню выбора типа игры"""
    global game_mode_f
    game_mode_f = False
    run = True
    while run:
        # Цикл обработки событий
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Проверяем входит ли координаты нажатия в границы кнопок
                response = [btn.click(event.pos, act, arg)
                            for btn, act, arg in game_mode_buttons]
                for x in response:
                    if len(x):
                        return x
                pg.time.delay(1)
        # Отрисовка меню выбора типа игры
        st_screen.fill((0, 0, 0))
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(tanks_battle,
                       (WIDTH / 2 - tanks_battle_rect.width / 2,
                        HEIGHT * 0.074))
        [i[0].draw(st_screen) for i in game_mode_buttons]
        st_screen.blit(cursor, pg.mouse.get_pos())
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def alpha_change_screen(surf_from, surf_to, alpha_from=0, alpha_to=255,
                        speed=3):
    """Анимация прорисовки задника"""
    surf_from.set_alpha(255)
    surf_to.set_alpha(0)
    alpha = 255
    alpha2 = 0
    while alpha2 < alpha_to and alpha > alpha_from:
        # Обработка событий
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_KP_ENTER:
                    surf_to.set_alpha(alpha_to)
                    screen.blit(surf_to, (0, 0))
                    return
        # Меняем прозрачность
        alpha2 += speed
        alpha2 = min(255, alpha2)
        alpha -= speed
        alpha = max(0, alpha)
        surf_to.set_alpha(alpha2)
        # Отрисовываем
        screen.blit(surf_from, (0, 0))
        screen.blit(surf_to, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def down_drop_text(surf, image, rect):
    """Анимация падения плашки 'Tanks Battle'"""
    # Функция, которая опускает картинку с текстом из-за
    # границы экрана в необходимое место
    y = -rect.height
    y_to = HEIGHT * 0.074
    orig_surf = surf.copy()
    while y < y_to:
        # Обработка событий
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_KP_ENTER:
                    return
        y += 4
        surf.blit(orig_surf, (0, 0))
        surf.blit(image, (WIDTH / 2 - rect.width / 2, y))
        screen.blit(surf, (0, 0))
        pg.display.flip()
        clock.tick(240)


def generate_rules():
    """Создание задника для меню правил"""
    width = WIDTH * 0.9
    height = HEIGHT * 0.8
    rules_back = pg.Surface((width, height))
    rules_back.fill((0, 0, 0))
    rules_back.set_alpha(200)
    # Шрифты
    font_header = pg.font.SysFont('comicsans', round(WIDTH * 0.021875))
    font_little_header = pg.font.SysFont('comicsans', round(WIDTH * 0.01875))
    font_default = pg.font.SysFont('comicsans', round(WIDTH * 0.015625))
    font_little_default = pg.font.SysFont('comicsans', round(WIDTH * 0.013541))

    # Заголовки
    header = font_header.render('Правила игры', True, (255, 255, 255))
    game_challenge = font_default.render('Задача игры: уничтожить все'
                                         ' вражеские танки и защитить свою'
                                         ' базу.', True, (255, 255, 255))
    field_tiles = font_little_header.render('Клетки поля:', True,
                                            (255, 255, 255))
    bonuses = font_little_header.render('Бонусы:', True,
                                        (255, 255, 255))

    # Текст для клетки кирпичной стены
    brick_tile = font_default.render('Кирпчиная стена', True,
                                     (255, 255, 255))
    brick_tile_desc1 = font_default.render('(сковзь нее нельзя проехать,',
                                           True,
                                           (255, 255, 255))
    brick_tile_desc2 = font_default.render(' но можно разрушить)', True,
                                           (255, 255, 255))

    # Текст для клетки железной стены
    armor_tile = font_default.render('Железная стена', True,
                                     (255, 255, 255))
    armor_tile_desc1 = font_default.render('(сквозь нее нельзя проехать', True,
                                           (255, 255, 255))
    armor_tile_desc2 = font_default.render(' и нельзя разрушить)', True,
                                           (255, 255, 255))

    # Текст для клетки леса
    forest_tile = font_default.render('Лес', True, (255, 255, 255))
    forest_desc_1 = font_default.render('(декоротивная клетка не', True,
                                        (255, 255, 255))
    forest_desc_2 = font_default.render(' влияющая на игру)', True,
                                        (255, 255, 255))

    # Текст для клетки воды
    water_tile = font_default.render('Вода', True, (255, 255, 255))
    water_desc_1 = font_default.render('(сквозь нее можно стрелять,', True,
                                       (255, 255, 255))
    water_desc_2 = font_default.render(' но нельзя проехать)', True,
                                       (255, 255, 255))

    # Текст для клетки гравия
    gravel_tile = font_default.render('Гравий', True, (255, 255, 255))
    gravel_desc = font_default.render('(обычная клетка)', True,
                                      (255, 255, 255))

    # Текст для часов
    clock_tile = font_little_default.render('Часы', True, (255, 255, 255))
    clock_desc = font_little_default.render(
        '(останавливают время для вражеских танков)', True, (255, 255, 255))

    # Текст для гранаты
    grenade_tile = font_little_default.render('Граната', True, (255, 255, 255))
    grenade_desc = font_little_default.render('(взрывает все вражеские танки)',
                                              True, (255, 255, 255))

    # Текст для шлема
    helmet_tile = font_little_default.render('Шлем', True, (255, 255, 255))
    helmet_desc = font_little_default.render('(создаёт одноразовую броню)',
                                             True, (255, 255, 255))

    # Текст для пистолета
    pistol_tile = font_little_default.render('Пистолет', True, (255, 255, 255))
    pistol_desc = font_little_default.render(
        '(даёт такну максимальный уровень)', True, (255, 255, 255))

    # Текст для лопаты
    shovel_tile = font_little_default.render('Лопата', True, (255, 255, 255))
    shovel_desc = font_little_default.render(
        '(создаёт временную броню вокруг базы)', True, (255, 255, 255))

    # Текст для звезды
    star_tile = font_little_default.render('Звезда', True, (255, 255, 255))
    star_desc = font_little_default.render(
        '(поднимает уровень такнка на один)', True, (255, 255, 255))

    # Текст для танка
    tank_tile = font_little_default.render('Танк', True, (255, 255, 255))
    tank_desc = font_little_default.render('(увеличивает количество жизней)',
                                           True, (255, 255, 255))

    arr = [pg.image.load('data/world/wall_1.png'),
           pg.image.load('data/world/metall_wall.png'),
           pg.image.load('data/world/tree.png'),
           pg.image.load('data/world/water.png'),
           pg.image.load('data/world/ground.png'),
           pg.transform.scale(
               pg.image.load('data/tanks_texture/bonus/clock.png'), (50, 50)),
           pg.transform.scale(
               pg.image.load('data/tanks_texture/bonus/grenade.png'),
               (50, 50)),
           pg.transform.scale(
               pg.image.load('data/tanks_texture/bonus/helmet.png'), (50, 50)),
           pg.transform.scale(
               pg.image.load('data/tanks_texture/bonus/pistol.png'), (50, 50)),
           pg.transform.scale(
               pg.image.load('data/tanks_texture/bonus/shovel.png'), (50, 50)),
           pg.transform.scale(
               pg.image.load('data/tanks_texture/bonus/star.png'), (50, 50)),
           pg.transform.scale(
               pg.image.load('data/tanks_texture/bonus/tank.png'), (50, 50))]

    # Заголовки
    rules_back.blit(header, ((width - header.get_width()) / 2, height * 0.03))
    rules_back.blit(field_tiles,
                    ((width - field_tiles.get_width()) / 2, height * 0.13))
    rules_back.blit(game_challenge, (width * 0.05, height * 0.08))
    rules_back.blit(bonuses, ((width - bonuses.get_width()) / 2, height * 0.5))

    # Картинки клеток
    rules_back.blit(arr[0], (width * 0.05, height * 0.2))
    rules_back.blit(arr[1], (width * 0.4, height * 0.2))
    rules_back.blit(arr[2], (width * 0.75, height * 0.2))
    rules_back.blit(arr[3], (width * 0.2, height * 0.33))
    rules_back.blit(arr[4], (width * 0.6, height * 0.33))

    # Картинки бонусов
    rules_back.blit(arr[5], (width * 0.05, height * 0.6))
    rules_back.blit(arr[6], (width * 0.4, height * 0.6))
    rules_back.blit(arr[7], (width * 0.75, height * 0.6))
    rules_back.blit(arr[8], (width * 0.05, height * 0.75))
    rules_back.blit(arr[9], (width * 0.4, height * 0.75))
    rules_back.blit(arr[10], (width * 0.75, height * 0.75))
    rules_back.blit(arr[11], (width * 0.4, height * 0.9))

    # Текст для клетки кирпичной стены
    rules_back.blit(brick_tile, (width * 0.05 + 90,
                                 height * 0.2 + 40 - brick_tile.get_height() -
                                 brick_tile_desc1.get_height() / 2))
    rules_back.blit(brick_tile_desc1, (width * 0.05 + 90, height * 0.2 + (
            80 - brick_tile_desc1.get_height()) / 2))
    rules_back.blit(brick_tile_desc2, (
        width * 0.05 + 90,
        height * 0.2 + 40 + brick_tile_desc1.get_height() / 2))

    # Текст для клеки железной стены
    rules_back.blit(armor_tile, (width * 0.4 + 90,
                                 height * 0.2 + 40 - armor_tile.get_height() -
                                 armor_tile_desc1.get_height() / 2))
    rules_back.blit(armor_tile_desc1, (
        width * 0.4 + 90,
        height * 0.2 + (80 - armor_tile_desc1.get_height()) / 2))
    rules_back.blit(armor_tile_desc2, (
        width * 0.4 + 90,
        height * 0.2 + 40 + armor_tile_desc1.get_height() / 2))

    # Текст для клетки леса
    rules_back.blit(forest_tile, (width * 0.75 + 90,
                                  height * 0.2 + 40 - forest_tile.get_height()
                                  - forest_desc_1.get_height() / 2))
    rules_back.blit(forest_desc_1, (
        width * 0.75 + 90,
        height * 0.2 + (80 - forest_desc_1.get_height()) / 2))
    rules_back.blit(forest_desc_2, (
        width * 0.75 + 90, height * 0.2 + 40 + forest_desc_1.get_height() / 2))

    # Текст для клетки воды
    rules_back.blit(water_tile, (width * 0.2 + 90,
                                 height * 0.33 + 40 - water_tile.get_height() -
                                 water_desc_1.get_height() / 2))
    rules_back.blit(water_desc_1, (
        width * 0.2 + 90,
        height * 0.33 + (80 - water_desc_1.get_height()) / 2))
    rules_back.blit(water_desc_2, (
        width * 0.2 + 90, height * 0.33 + 40 + water_desc_1.get_height() / 2))

    # Текст для клетки гравия
    rules_back.blit(gravel_tile, (
        width * 0.6 + 90, height * 0.33 + 40 - gravel_tile.get_height()))
    rules_back.blit(gravel_desc, (width * 0.6 + 90, height * 0.33 + 40))

    # Текст для часов
    rules_back.blit(clock_tile, (
        width * 0.05 + 60, height * 0.6 + 25 - clock_tile.get_height()))
    rules_back.blit(clock_desc, (width * 0.05 + 60, height * 0.6 + 25))

    # Текст для гранаты
    rules_back.blit(grenade_tile, (
        width * 0.4 + 60, height * 0.6 + 25 - grenade_tile.get_height()))
    rules_back.blit(grenade_desc, (width * 0.4 + 60, height * 0.6 + 25))

    # Текст для шлема
    rules_back.blit(helmet_tile, (
        width * 0.75 + 60, height * 0.6 + 25 - helmet_tile.get_height()))
    rules_back.blit(helmet_desc, (width * 0.75 + 60, height * 0.6 + 25))

    # Текст для пистолета
    rules_back.blit(pistol_tile, (
        width * 0.05 + 60, height * 0.75 + 25 - pistol_tile.get_height()))
    rules_back.blit(pistol_desc, (width * 0.05 + 60, height * 0.75 + 25))

    # Текст для лопаты
    rules_back.blit(shovel_tile, (
        width * 0.4 + 60, height * 0.75 + 25 - shovel_tile.get_height()))
    rules_back.blit(shovel_desc, (width * 0.4 + 60, height * 0.75 + 25))

    # Текст для звезды
    rules_back.blit(star_tile, (
        width * 0.75 + 60, height * 0.75 + 25 - star_tile.get_height()))
    rules_back.blit(star_desc, (width * 0.75 + 60, height * 0.75 + 25))

    # Текст для танка
    rules_back.blit(tank_tile, (
        width * 0.4 + 60, height * 0.9 + 25 - tank_tile.get_height()))
    rules_back.blit(tank_desc, (width * 0.4 + 60, height * 0.9 + 25))

    return rules_back


def rules_screen():
    """Окно правил"""
    run = True
    rls_screen = generate_rules()
    while run:
        # Цикл обработки событий
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                response = [btn.click(event.pos, act, arg)
                            for btn, act, arg in rules_btn]
                for x in response:
                    if len(x):
                        return x
                pg.time.delay(1)
        # Отрисовка меню настроек
        st_screen.fill((0, 0, 0))
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(bck_dark, (0, 0))
        st_screen.blit(rls_screen, (WIDTH * 0.05, HEIGHT * 0.05))
        [i[0].draw(st_screen) for i in rules_btn]
        st_screen.blit(cursor, pg.mouse.get_pos())
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def first_show():
    """Анимация запуска игры"""
    time.sleep(1)
    pg.mixer.music.play(loops=-1)
    alpha_change_screen(background, bg_screen, alpha_to=255 // 3)
    st_screen.blit(bg_screen, (0, 0))
    down_drop_text(screen, tanks_battle, tanks_battle_rect)


def play_music():
    """Запуск музыки"""
    pg.mixer.music.play(loops=-1)
    return [start_screen, False]


def start_screen(is_first):
    """Главное окно меню"""
    global bck_is_drk
    pg.mouse.set_visible(False)
    first_show() if is_first == 2 else None
    run = True
    while run:
        st_screen.fill((0, 0, 0))
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(tanks_battle,
                       (WIDTH / 2 - tanks_battle_rect.width / 2,
                        HEIGHT * 0.074))
        # Цикл обработки событий
        if pause:
            [i[0].draw(st_screen, flag=False) for i in main_menu_buttons]
            # Если стоит паузка, значит открыто одно из окон
            # Накладываем темный фильтр
            st_screen.blit(bck_dark, (0, 0))
            # Проверка на то, какое окно открыто
            if exit_wnd_f:
                exit_window.draw(st_screen)
            if settings_wnd_f:
                setting_window.draw(st_screen)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    terminate()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # Проверяем кнопки в зависимости от открытого окна
                    if exit_wnd_f:
                        response = [btn.click(event.pos, act, arg)
                                    for btn, act, arg in close_win_buttons]
                        for x in response:
                            if len(x):
                                return x
                    if settings_wnd_f:
                        response = [btn.click(event.pos, act, arg) for
                                    btn, act, arg in settings_wnd_btns]
                        for x in response:
                            if len(x):
                                return x
                # Входит ли событие в прямоугольники полей ввода
                if settings_wnd_f:
                    [i.handle_event(event) for i in
                     setting_window.line_edits_arr]
            # Входит ли событие в прямоугольники микшеров громкости
            if settings_wnd_f:
                if pg.mouse.get_pressed()[0]:
                    setting_window.music_bar.click(pg.mouse.get_pos())
                    setting_window.effects_bar.click(pg.mouse.get_pos())
                [(i.draw(st_screen)) for i in setting_window.line_edits_arr]
            # Отрисовка кнопок в зависимости от окна
            if exit_wnd_f:
                [i[0].draw(st_screen) for i in close_win_buttons]
            if settings_wnd_f:
                [i[0].draw(st_screen) for i in settings_wnd_btns]
            st_screen.blit(cursor, pg.mouse.get_pos())
            screen.blit(st_screen, (0, 0))
            pg.display.flip()
            clock.tick(FPS)
            continue
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    terminate()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # Проерка на вхождение координат события в прямоугольник
                    # кнопок
                    response = [btn.click(event.pos, act, arg)
                                for btn, act, arg in main_menu_buttons]
                    for x in response:
                        if len(x):
                            return x
                    pg.time.delay(1)
        # Отрисовка главного меню
        [i[0].draw(st_screen) for i in main_menu_buttons]
        st_screen.blit(cursor, pg.mouse.get_pos())
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)
        bck_is_drk = False


# Список кнопок главного меню
main_menu_buttons = [[Button('Играть', WIDTH * 0.34, HEIGHT * 0.5,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), game_mode_screen,
                      (False,)],
                     [Button('Настройки', WIDTH * 0.34, HEIGHT * 0.574,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), change_settings_f,
                      (False,)],
                     [Button('Правила', WIDTH * 0.34, HEIGHT * 0.648,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), rules_screen,
                      (False,)],
                     [Button('Выход', WIDTH * 0.34, HEIGHT * 0.722,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), change_exit_f,
                      (False,)]]

# Список кнопок окна закрытия
close_win_buttons = [[Button('Выйти', int(WIDTH / 2 - 0.1 * WIDTH),
                             int(HEIGHT / 2 + 0.15 * HEIGHT / 4),
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=20), terminate, (False,)],
                     [Button('Отмена', int(WIDTH / 2),
                             int(HEIGHT / 2 + 0.15 * HEIGHT / 4),
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=20), change_exit_f, (False,)]]

# Создание экземпляра класса окон подтверждения и настроек
exit_window = ConfirmWindow('Подтвреждение', 'Вы действительно хотите выйти?')
setting_window = SettingsWindow()

# Кнопки меню выбора типа игры
game_mode_buttons = [[Button('Играть', WIDTH * 0.34, HEIGHT * 0.5,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), choose_level_screen,
                      (1,)],
                     [Button('Игра с другом', WIDTH * 0.34, HEIGHT * 0.574,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), choose_level_screen,
                      (2,)],
                     [Button('Назад', WIDTH * 0.34, HEIGHT * 0.648,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), start_screen, (1,)]]

# Кнопки окна настроек
settings_wnd_btns = [[Button('Сохранить', WIDTH * 0.491666, HEIGHT * 0.682407,
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=round(WIDTH * 0.010416), limit=(20, 0)),
                      setting_window.saving, (False,)],
                     [Button('Назад', WIDTH * 0.5697916, HEIGHT * 0.682407,
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=round(WIDTH * 0.010416), limit=(20, 0)),
                      change_settings_f, (False,)],
                     [Button('По умолчанию', WIDTH * 0.4135416,
                             HEIGHT * 0.682407, width=int(WIDTH * 0.1),
                             height=int(HEIGHT * 0.03),
                             size=round(WIDTH * 0.010416), limit=(20, 0)),
                      default_settings, (False,)]]

# Кнопки меню выбора уровня 1 типа игры
lvl_scrn_buttons_1 = [[Button('Уровень 1', 0, HEIGHT * 0.06,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_1',)],
                      [Button('Уровень 2', 0, HEIGHT * 0.13,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_2',)],
                      [Button('Уровень 3', 0, HEIGHT * 0.20,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_3',)],
                      [Button('Уровень 4', 0, HEIGHT * 0.27,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_4',)],
                      [Button('Уровень 5', 0, HEIGHT * 0.34,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_5',)],
                      [Button('Уровень 6', 0, HEIGHT * 0.41,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_6',)],
                      [Button('Уровень 7', 0, HEIGHT * 0.48,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_7',)],
                      [Button('Уровень 8', 0, HEIGHT * 0.55,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_8',)],
                      [Button('Уровень 9', 0, HEIGHT * 0.62,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_9',)],
                      [Button('Уровень 10', 0, HEIGHT * 0.69,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_10',)],
                      [Button('Уровень 11', WIDTH * 0.2083333, HEIGHT * 0.06,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_11',)],
                      [Button('Уровень 12', WIDTH * 0.2083333, HEIGHT * 0.13,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_12',)],
                      [Button('Уровень 13', WIDTH * 0.2083333, HEIGHT * 0.20,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_13',)],
                      [Button('Уровень 14', WIDTH * 0.2083333, HEIGHT * 0.27,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_14',)],
                      [Button('Уровень 15', WIDTH * 0.2083333, HEIGHT * 0.34,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_15',)],
                      [Button('Уровень 16', WIDTH * 0.2083333, HEIGHT * 0.41,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_16',)],
                      [Button('Уровень 17', WIDTH * 0.2083333, HEIGHT * 0.48,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_17',)],
                      [Button('Уровень 18', WIDTH * 0.2083333, HEIGHT * 0.55,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_18',)],
                      [Button('Уровень 19', WIDTH * 0.2083333, HEIGHT * 0.62,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_19',)],
                      [Button('Уровень 20', WIDTH * 0.2083333, HEIGHT * 0.69,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('1_20',)],
                      [Button('Назад', WIDTH * 0.04427083, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), game_mode_screen,
                       (False,)],
                      [Button('Играть', WIDTH * 0.611979166, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), start_game,
                       (False,)]]

# Кнопки меню выбора уровня 2 типа игры
lvl_scrn_buttons_2 = [[Button('Уровень 1', 0, HEIGHT * 0.06,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_1',)],
                      [Button('Уровень 2', 0, HEIGHT * 0.13,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_2',)],
                      [Button('Уровень 3', 0, HEIGHT * 0.20,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_3',)],
                      [Button('Уровень 4', 0, HEIGHT * 0.27,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_4',)],
                      [Button('Уровень 5', 0, HEIGHT * 0.34,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_5',)],
                      [Button('Уровень 6', 0, HEIGHT * 0.41,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_6',)],
                      [Button('Уровень 7', 0, HEIGHT * 0.48,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_7',)],
                      [Button('Уровень 8', 0, HEIGHT * 0.55,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_8',)],
                      [Button('Уровень 9', 0, HEIGHT * 0.62,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_9',)],
                      [Button('Уровень 10', 0, HEIGHT * 0.69,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_10',)],
                      [Button('Уровень 11', WIDTH * 0.2083333, HEIGHT * 0.06,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_11',)],
                      [Button('Уровень 12', WIDTH * 0.2083333, HEIGHT * 0.13,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_12',)],
                      [Button('Уровень 13', WIDTH * 0.2083333, HEIGHT * 0.20,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_13',)],
                      [Button('Уровень 14', WIDTH * 0.2083333, HEIGHT * 0.27,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_14',)],
                      [Button('Уровень 15', WIDTH * 0.2083333, HEIGHT * 0.34,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_15',)],
                      [Button('Уровень 16', WIDTH * 0.2083333, HEIGHT * 0.41,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_16',)],
                      [Button('Уровень 17', WIDTH * 0.2083333, HEIGHT * 0.48,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_17',)],
                      [Button('Уровень 18', WIDTH * 0.2083333, HEIGHT * 0.55,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_18',)],
                      [Button('Уровень 19', WIDTH * 0.2083333, HEIGHT * 0.62,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_19',)],
                      [Button('Уровень 20', WIDTH * 0.2083333, HEIGHT * 0.69,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05),
                              limit=(WIDTH * 0.046875, 0)), change_lvl_image,
                       ('2_20',)],
                      [Button('Назад', WIDTH * 0.04427083, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), game_mode_screen,
                       (False,)],
                      [Button('Играть', WIDTH * 0.611979166, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), start_game,
                       (False,)]]

# Кнопка меню правил
rules_btn = [
    [Button('Назад', WIDTH * 0.33958, HEIGHT * 0.9), start_screen, (1,)]]


def main():
    """Главный цикл игры"""
    running = True
    response = start_screen(2)
    while running:
        if len(response) == 2:
            response = response[0](response[1])
        else:
            response = response[0]()
    pg.quit()


if __name__ == '__main__':
    main()
