import pygame as pg
import sys
import time
import json

FPS = 240
pg.init()
display_info = pg.display.Info()
WIDTH, HEIGHT = display_info.current_w, display_info.current_h
screen = pg.display.set_mode((WIDTH, HEIGHT))
background = pg.Surface((WIDTH, HEIGHT))
background.fill((0, 0, 0, 0))
pg.display.set_caption('Tanks Battle')
clock = pg.time.Clock()
maps = ['']
pg.mixer.music.load('../data/music/music/main_theme.mp3')
click_sound = pg.mixer.Sound('../data/sounds/click.wav')
with open('../settings/settings.json') as f:
    data = json.load(f)
    music_v = data['player_settings']['music'] / 100
    sound_v = data['player_settings']['effects'] / 100
pg.mixer.music.set_volume(music_v)
click_sound.set_volume(sound_v)
SYSTEM_IMAGES = 'data\\system_image\\'
fon = pg.transform.scale(pg.image.load('../data/system_image'
                                       '/main_menu_bckgrnd.png'), (WIDTH,
                                                                   HEIGHT))
st_screen = pg.Surface(screen.get_size())
bg_screen = pg.Surface(screen.get_size())
bg_screen.blit(fon, (0, 0))
lvl_scr = pg.transform.scale(pg.image.load('../data/system_image'
                                           '/main_menu_bckgrnd.png'),
                             (WIDTH, HEIGHT))
lvl_scrn = pg.Surface(screen.get_size())
lvl_scrn.blit(lvl_scr, (0, 0))
lvl_image = None
border = pg.transform.scale(pg.image.load('../data/system_image/'
                                          'border.png'), (
                            round(WIDTH * 0.390625),
                            round(HEIGHT * 0.6944444)))
tanks_battle = pg.image.load('../data/system_image/TanksBattle.png')
tanks_battle_rect = tanks_battle.get_rect()
bck_dark = pg.Surface((WIDTH, HEIGHT))
bck_dark.fill((0, 0, 0))
bck_dark.set_alpha(100)
map_index = (1, 1)
pause = False
exit_wnd_f = False
settings_wnd_f = False
rules_wnd_f = False
is_save = False
bck_is_drk = False


def terminate():
    pg.quit()
    sys.exit()


def change_exit_f():
    global exit_wnd_f
    exit_wnd_f = not exit_wnd_f
    change_pause()
    return [start_screen, (False,)]


def change_settings_f():
    global settings_wnd_f, setting_window, is_save
    settings_wnd_f = not settings_wnd_f
    pg.mixer.music.set_volume(music_v)
    click_sound.set_volume(sound_v)
    if settings_wnd_f:
        setting_window.update()
    change_pause()
    return [start_screen, (False,)]


def default_settings():
    global setting_window
    with open('../settings/default_settings.json') as f:
        data = json.load(f)
        with open('../settings/settings.json', 'w') as f1:
            json.dump(data, f1)
    setting_window.update()
    return [start_screen, (False,)]


def change_pause():
    global pause
    pause = not pause


def change_lvl_image(index):
    global lvl_image, map_index
    map_index = list(map(int, index.split('_')))
    print(index)
    lvl_image = pg.transform.scale(
        pg.image.load(f'../data/system_image/lvl{index}.jpg'),
        (round(WIDTH * 0.32447916), round(HEIGHT * 0.56296)))
    return [choose_level_screen, (map_index[0],)]


class InputBox:
    def __init__(self, x, y, w, h, text='', centering=False, usual=True,
                 btn=False):
        self.color_inactive = (55, 56, 56)
        self.color_active = (0, 0, 0)
        self.font = pg.font.Font(None, round(w * 0.2285714))
        self.rect = pg.Rect(x, y, w, h)
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.inactive_border = 2
        self.active_border = 3
        self.border = 2
        self.usual = usual
        self.centering = centering
        self.btn = btn

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active\
                else self.color_inactive
            self.border = self.active_border if self.active\
                else self.inactive_border
        if self.active and not self.usual:
            self.text = ''
        if event.type == pg.KEYDOWN:
            if self.active:
                if self.usual:
                    if event.key == pg.K_RETURN:
                        self.text = ''
                    elif event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode
                else:
                    self.text = pg.key.name(event.key)
                    self.text = f'keypad ' \
                                f'{self.text.split("[")[1].split("]")[0]}'\
                        if '[' in self.text or ']' in self.text else self.text
                    self.btn = event.key
                    self.active = False
        self.text = self.text[:10]
        self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        if not self.centering:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        else:
            screen.blit(self.txt_surface, (
            self.rect.x + (self.rect.w - self.txt_surface.get_width()) / 2,
            self.rect.y + 5))
        pg.draw.rect(screen, self.color, self.rect, self.border)


class SliderBar:
    def __init__(self, x, y, width, height, orientation, value=100, music=0):
        self.x, self.y = x, y
        self.width, self.height = (width, height) if orientation else (
        height, width)
        self.post = pg.Surface(
            (self.width / 3, self.height + self.height / 25))
        self.slider = pg.Surface((self.width, self.height / 25))
        self.post.fill((47, 48, 48))
        self.slider.fill((84, 87, 87))
        self.bar = pg.transform.scale(pg.image.load('../data/system_image/'
                                                    'alpha_0.png'), (
                                      self.width,
                                      int(self.height + self.height / 25)))
        self.bar.blit(self.post, (self.width / 3, 0))
        self.pxperv = self.height / 100
        self.value = value
        self.music = music

    def draw(self):
        returning = self.bar.copy()
        returning.blit(self.slider,
                       (0, self.height - self.value * self.pxperv))
        return returning

    def click(self, pos):
        x, y = pos
        if self.x - 10 <= x <= self.x + self.width + 10 and\
                self.y <= y <= self.y + self.height:
            self.value = 100 - (y - self.y) / self.pxperv
            if not self.music:
                pg.mixer.music.set_volume(self.value / 100)
            elif self.music == 1:
                click_sound.set_volume(self.value / 100)


class SettingsWindow:
    def __init__(self):
        self.width, self.height = WIDTH // 3, round(HEIGHT * 0.4)
        self.background = pg.transform.scale(
            pg.image.load('../data/system_image/'
                          'settings_wnd_bckgrnd.jpg'),
            (self.width, self.height))
        self.top = pg.Surface((self.width, self.height / 8))
        self.top.fill((70, 70, 68))
        self.window_scr = pg.Surface((self.width, self.height))
        self.none_button = False
        self.create_background()

    def create_background(self):
        font_head = pg.font.SysFont("comicsans", round(0.059375 * self.width))
        font = pg.font.SysFont("comicsans", round(0.0421875 * self.width))
        font_little_head = pg.font.SysFont("comicsans",
                                           round(0.046875 * self.width))
        font_little = pg.font.SysFont("comicsans",
                                      round(0.0390625 * self.width))
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
        self.background.blit(self.top, (0, 0))
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
        self.window_scr.blit(self.background, (0, 0))
        if self.none_button:
            self.window_scr.blit(self.none_button_text1, (
            self.width * 0.0234375, self.height * 0.90277777))
            self.window_scr.blit(self.none_button_text2, (
            self.width * 0.0234375, self.height * 0.949074))
        self.window_scr.blit(self.music_bar.draw(),
                             (self.width * 0.078125, self.height * 0.162037))
        self.window_scr.blit(self.effects_bar.draw(),
                             (self.width * 0.234375, self.height * 0.162037))
        win.blit(self.window_scr,
                 ((WIDTH - self.width) / 2, (HEIGHT - self.height) / 1.883720))

    def update(self):
        self.none_button = False
        with open('../settings/settings.json') as file:
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
        pg.mixer.music.set_volume(data["player_settings"]["music"] / 100)
        click_sound.set_volume(data["player_settings"]["effects"] / 100)
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
        global is_save, music_v, sound_v
        is_save = True
        if any([not x.text for x in self.line_edits_arr]):
            self.none_button = True
            return
        with open('../settings/settings.json') as f:
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
        music_v, sound_v = self.music_bar.value / 100, self.effects_bar.value\
                           / 100
        pg.mixer.music.set_volume(music_v)
        click_sound.set_volume(sound_v)
        with open('../settings/settings.json', 'w') as f:
            json.dump(data, f)
        self.update()
        return [start_screen, (False,)]


class ConfirmWindow:
    def __init__(self, header_text, confirm_text):
        self.header_text = header_text
        self.confirm_text = confirm_text
        self.width, self.height = int(0.187 * WIDTH), int(0.15 * HEIGHT)
        self.background = pg.Surface((self.width, self.height))
        self.top = pg.Surface((self.width, self.height / 6))
        self.top.fill((70, 70, 68))
        self.background.fill((147, 145, 142))
        self.window_scr = pg.Surface((self.width, self.height))

    def draw(self, win):
        font_head = pg.font.SysFont("comicsans", round(0.015625 * WIDTH))
        font_conf = pg.font.SysFont("comicsans", round(0.013 * WIDTH))
        header_text = font_head.render(self.header_text, True, (255, 255, 255))
        confirm_text = font_conf.render(self.confirm_text, True, (15, 15, 14))
        self.window_scr.blit(self.background, (0, 0))
        self.window_scr.blit(self.top, (0, 0))
        self.window_scr.blit(header_text, (
        (self.width - header_text.get_width()) / 2, self.height * 0.03))
        self.window_scr.blit(confirm_text, (
        (self.width - confirm_text.get_width()) / 2, self.height / 4.5))
        pg.draw.line(self.window_scr, (57, 59, 61), (0, self.height * 0.16),
                     (self.width, self.height * 0.16), 3)
        pg.draw.rect(self.window_scr, (57, 59, 61),
                     (0, 0, self.width, self.height), 6)
        win.blit(self.window_scr,
                 ((WIDTH - self.width) / 2 + 2, (HEIGHT - self.height) / 2))


class Button:
    def __init__(self, text, x, y, width=round(WIDTH * 0.32083),
                 height=round(HEIGHT * 0.0629629), size=round(WIDTH * 0.02083),
                 limit=(0, 0)):
        self.x = x
        self.y = y
        self.limit_x = limit[0]
        self.limit_y = limit[1]
        self.size = size
        self.normal_image = pg.transform.scale(
            pg.image.load('../data/system_image/'
                          'button_normal.png'), (width, height))
        self.hover_image = pg.transform.scale(
            pg.image.load('../data/system_image/'
                          'button_hovered.png'), (width, height))
        self.width, self.height = self.normal_image.get_rect().size
        font = pg.font.SysFont("comicsans", self.size)
        self.text = font.render(text, True, (255, 255, 255))

    def draw(self, win):
        x1, y1 = pg.mouse.get_pos()

        if self.x + self.limit_x <= x1 <= self.x + self.width - self.limit_x\
                and self.y <= y1 <= self.y + self.height:
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
        x1, y1 = pos[0], pos[1]
        if (
                self.x + self.limit_x <= x1 <= self.x + self.width -
                self.limit_x and self.y <= y1 <= self.y + self.height) and\
                action:
            click_sound.play()
            if args[0][0]:
                return [action, args[0][0]]
            else:
                return [action]
        else:
            return []


def choose_level_screen(typ):
    global lvl_image
    if not lvl_image:
        if (type(typ) == tuple and typ[0] == 1) or typ == 1:
            lvl_image = pg.transform.scale(pg.image.load('../data'
                                                         '/system_image'
                                                         '/lvl1_1.jpg'),
                                           (round(WIDTH * 0.32447916),
                                            round(HEIGHT * 0.56296)))
        else:
            lvl_image = pg.transform.scale(pg.image.load('../data'
                                                         '/system_image'
                                                         '/lvl2_1.jpg'),
                                           (round(WIDTH * 0.32447916),
                                            round(HEIGHT * 0.56296)))
    print('typ', typ)
    run = True
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if (type(typ) == tuple and typ[0] == 1) or typ == 1:
                    response = [btn.click(event.pos, act, arg)
                                for btn, act, arg in lvl_scrn_buttons_1]
                else:
                    response = [btn.click(event.pos, act, arg)
                                for btn, act, arg in lvl_scrn_buttons_2]
                for x in response:
                    if len(x):
                        return x
                pg.time.delay(1)
        st_screen.fill((0, 0, 0))
        st_screen.blit(bg_screen, (0, 0))
        if typ:
            [i[0].draw(st_screen) for i in lvl_scrn_buttons_1]
        else:
            [i[0].draw(st_screen) for i in lvl_scrn_buttons_2]
        st_screen.blit(lvl_image, (WIDTH * 0.60677083, HEIGHT * 0.1185))
        st_screen.blit(border, (WIDTH * 0.57291666, HEIGHT * 0.05))
        pg.draw.rect(st_screen, (57, 59, 61), (round(WIDTH * 0.57291666), round(HEIGHT * 0.05), round(WIDTH * 0.390625), round(HEIGHT * 0.6944444)), 6)
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def game_mode_screen():
    run = True
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                response = [btn.click(event.pos, act, arg)
                            for btn, act, arg in game_mode_buttons]
                for x in response:
                    if len(x):
                        return x
                pg.time.delay(1)
        st_screen.fill((0, 0, 0))
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(tanks_battle,
                       (WIDTH / 2 - tanks_battle_rect.width / 2,
                        HEIGHT * 0.074))
        [i[0].draw(st_screen) for i in game_mode_buttons]
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def alpha_change_screen(surf_from, surf_to, alpha_from=0, alpha_to=255,
                        speed=3):
    surf_from.set_alpha(255)
    surf_to.set_alpha(0)
    alpha = 255
    alpha2 = 0
    while alpha2 < alpha_to and alpha > alpha_from:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_KP_ENTER:
                    surf_to.set_alpha(alpha_to)
                    screen.blit(surf_to, (0, 0))
                    return
        alpha2 += speed
        alpha2 = min(255, alpha2)
        alpha -= speed
        alpha = max(0, alpha)
        surf_to.set_alpha(alpha2)
        screen.blit(surf_from, (0, 0))
        screen.blit(surf_to, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def down_drop_text(surf, image, rect):
    # Функция, которая опускает картинку с текстом из-за
    # границы экрана в необходимое место
    y = -rect.height
    y_to = HEIGHT * 0.074
    orig_surf = surf.copy()
    while y < y_to:
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


def first_show():
    time.sleep(1)
    pg.mixer.music.play(loops=-1)
    alpha_change_screen(background, bg_screen, alpha_to=255 // 3)
    st_screen.blit(bg_screen, (0, 0))
    down_drop_text(screen, tanks_battle, tanks_battle_rect)


def start_screen(is_first):
    global bck_is_drk
    first_show() if is_first == 2 else None
    run = True
    while run:
        if pause:
            if not bck_is_drk:
                screen.blit(bck_dark, (0, 0))
                bck_is_drk = True
            if exit_wnd_f:
                exit_window.draw(screen)
            if settings_wnd_f:
                setting_window.draw(screen)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    terminate()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
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
                if settings_wnd_f:
                    [i.handle_event(event) for i in
                     setting_window.line_edits_arr]
            if settings_wnd_f:
                if pg.mouse.get_pressed()[0]:
                    setting_window.music_bar.click(pg.mouse.get_pos())
                    setting_window.effects_bar.click(pg.mouse.get_pos())
                [(i.draw(screen)) for i in setting_window.line_edits_arr]
            if exit_wnd_f:
                [i[0].draw(screen) for i in close_win_buttons]
            if settings_wnd_f:
                [i[0].draw(screen) for i in settings_wnd_btns]
            pg.display.flip()
            clock.tick(FPS)
            continue
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    terminate()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    response = [btn.click(event.pos, act, arg)
                                for btn, act, arg in main_menu_buttons]
                    for x in response:
                        if len(x):
                            return x
                    pg.time.delay(1)
        st_screen.fill((0, 0, 0))
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(tanks_battle,
                       (WIDTH / 2 - tanks_battle_rect.width / 2,
                        HEIGHT * 0.074))
        [i[0].draw(st_screen) for i in main_menu_buttons]
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)
        bck_is_drk = False


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
                             height=int(0.063 * HEIGHT)), False, (False,)],
                     [Button('Выход', WIDTH * 0.34, HEIGHT * 0.722,
                             width=int(0.321 * WIDTH),
                             height=int(0.063 * HEIGHT)), change_exit_f,
                      (False,)]]

close_win_buttons = [[Button('Выйти', int(WIDTH / 2 - 0.1 * WIDTH),
                             int(HEIGHT / 2 + 0.15 * HEIGHT / 4),
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=20), terminate, (False,)],
                     [Button('Отмена', int(WIDTH / 2),
                             int(HEIGHT / 2 + 0.15 * HEIGHT / 4),
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=20), change_exit_f, (False,)]]

exit_window = ConfirmWindow('Подтвреждение', 'Вы действительно хотите выйти?')
setting_window = SettingsWindow()

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

lvl_scrn_buttons_1 = [[Button('Уровень 1', WIDTH * 0.125, HEIGHT * 0.06,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_1',)],
                      [Button('Уровень 2', WIDTH * 0.125, HEIGHT * 0.13,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_2',)],
                      [Button('Уровень 3', WIDTH * 0.125, HEIGHT * 0.20,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_3',)],
                      [Button('Уровень 4', WIDTH * 0.125, HEIGHT * 0.27,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_4',)],
                      [Button('Уровень 5', WIDTH * 0.125, HEIGHT * 0.34,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_5',)],
                      [Button('Уровень 6', WIDTH * 0.125, HEIGHT * 0.41,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_6',)],
                      [Button('Уровень 7', WIDTH * 0.125, HEIGHT * 0.48,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_7',)],
                      [Button('Уровень 8', WIDTH * 0.125, HEIGHT * 0.55,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_8',)],
                      [Button('Уровень 9', WIDTH * 0.125, HEIGHT * 0.62,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_9',)],
                      [Button('Уровень 10', WIDTH * 0.125, HEIGHT * 0.69,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('1_10',)],
                      [Button('Назад', WIDTH * 0.08957, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), game_mode_screen,
                       (False,)],
                      [Button('Играть', WIDTH * 0.611979166, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), False, (False,)]]

lvl_scrn_buttons_2 = [[Button('Уровень 1', WIDTH * 0.125, HEIGHT * 0.06,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_1',)],
                      [Button('Уровень 2', WIDTH * 0.125, HEIGHT * 0.13,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_2',)],
                      [Button('Уровень 3', WIDTH * 0.125, HEIGHT * 0.20,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_3',)],
                      [Button('Уровень 4', WIDTH * 0.125, HEIGHT * 0.27,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_4',)],
                      [Button('Уровень 5', WIDTH * 0.125, HEIGHT * 0.34,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_5',)],
                      [Button('Уровень 6', WIDTH * 0.125, HEIGHT * 0.41,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_6',)],
                      [Button('Уровень 7', WIDTH * 0.125, HEIGHT * 0.48,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_7',)],
                      [Button('Уровень 8', WIDTH * 0.125, HEIGHT * 0.55,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_8',)],
                      [Button('Уровень 9', WIDTH * 0.125, HEIGHT * 0.62,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_9',)],
                      [Button('Уровень 10', WIDTH * 0.125, HEIGHT * 0.69,
                              width=int(WIDTH * 0.25),
                              height=int(HEIGHT * 0.05), limit=(90, 0)),
                       change_lvl_image, ('2_10',)],
                      [Button('Назад', WIDTH * 0.089583, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), game_mode_screen,
                       (False,)],
                      [Button('Играть', WIDTH * 0.611979166, HEIGHT * 0.85,
                              width=int(0.321 * WIDTH),
                              height=int(0.063 * HEIGHT)), False, (False,)]]


def main():
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
