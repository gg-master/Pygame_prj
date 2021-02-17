from constants import *
from globals import *
from default_funcs import *
import pygame as pg
import pygame_gui
import sys
import os
import time
import json

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
background = pg.Surface((WIDTH, HEIGHT))
background.fill((0, 0, 0, 0))
pg.display.set_caption(CAPTION)
clock = pg.time.Clock()
maps = ['']
pg.mixer.music.load(MAIN_MENU_MUSIC_PATH)
pg.mixer.music.set_volume(0.01)
click_sound = pg.mixer.Sound(CLICK_BUTTON_SOUND_PATH)
fon = pg.transform.scale(load_image('fon5.png'), (WIDTH, HEIGHT))
st_screen = pg.Surface(screen.get_size())
bg_screen = pg.Surface(screen.get_size())
bg_screen.blit(fon, (0, 0))
lvl_scrn = pg.transform.scale(pg.image.load('style/data/system_image/'
                                         'ch_lvl_scrn_back.png'), (WIDTH, HEIGHT))
border = pg.transform.scale(pg.image.load('style/data/system_image/'
                                         'new_border.png'), (750, 750))
tanks_battle = load_image(GAME_HEADER_PATH)
tanks_battle_rect = tanks_battle.get_rect()
bck_dark = pg.Surface((WIDTH, HEIGHT))
bck_dark.fill((0, 0, 0))
bck_dark.set_alpha(100)
pause = False
exit_wnd_f = False
settings_wnd_f = False
rules_wnd_f = False

COLOR_INACTIVE = (55, 56, 56)
COLOR_ACTIVE = (0, 0, 0)


def change_exit_f():
    global exit_wnd_f
    exit_wnd_f = not exit_wnd_f
    return change_pause()
    # return wnd_manager()


def change_settings_f():
    global settings_wnd_f, setting_window
    settings_wnd_f = not settings_wnd_f
    if settings_wnd_f:
        setting_window.update()
    return change_pause()


def default_settings():
    global setting_window
    with open('settings2.json') as f:
        data = json.load(f)
        with open('settings.json', 'w') as f1:
            json.dump(data, f1)
    setting_window.update()

# def wnd_manager(exit=False, settings=False, rules=False):
#     change_pause()
#     if exit_wnd_f:
#         return exit_window.draw(screen)
#     if settings_wnd_f:
#         return
#     if rules_wnd_f:
#         return


def change_pause():
    global pause
    pause = not pause


class InputBox:
    def __init__(self, x, y, w, h, text='', centering=False, usual=True, btn=False):
        FONT = pg.font.Font(None, 32)
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.inactive_border = 2
        self.active_border = 3
        self.border = 2
        self.usual = usual
        self.centering = centering
        self.btn = btn

    def handle_event(self, event):
        FONT = pg.font.Font(None, 32)
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            self.border = self.active_border if self.active else self.inactive_border
        if self.active and not self.usual:
            self.text = ''
        if event.type == pg.KEYDOWN:
            if self.active:
                if self.usual:
                    if event.key == pg.K_RETURN:
                        print(self.text)
                        self.text = ''
                    elif event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode
                else:
                    self.text = pg.key.name(event.key)
                    self.btn = event.key
                    self.active = False
        self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        pass
        # Resize the box if the text is too long.
        # width = max(self.rect.width, self.txt_surface.get_width()+10)
        # self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        if not self.centering:
            screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        else:
            screen.blit(self.txt_surface, (self.rect.x + (self.rect.w - self.txt_surface.get_width()) / 2, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, self.border)


class SliderBar:
    def __init__(self, x, y, width, height, orientation, value=100):
        self.x, self.y = x, y
        self.width, self.height = (width, height) if orientation else (height, width)
        self.post = pg.Surface((self.width / 3, self.height + self.height / 25))
        self.slider = pg.Surface((self.width, self.height / 25))
        self.post.fill((47, 48, 48))
        self.slider.fill((84, 87, 87))
        self.bar = pg.transform.scale(pg.image.load('style/data/system_image/'
                                         'alpha_fon.png'), (self.width, int(self.height + self.height / 25)))
        self.bar.blit(self.post, (self.width / 3, 0))
        self.pxperv = self.height / 100
        self.value = value

    def draw(self):
        returning = self.bar.copy()
        returning.blit(self.slider, (0, self.height - self.value * self.pxperv))
        return returning

    def click(self, pos):
        x, y = pos
        if self.x - 10 <= x <= self.x + self.width + 10 and self.y <= y <= self.y + self.height:
            self.value = 100 - (y - self.y) / self.pxperv


class SettingsWindow:
    def __init__(self):
        self.width, self.height = WIDTH // 3, round(HEIGHT * 0.4)
        self.background = pg.transform.scale(pg.image.load('style/data/system_image/'
                                         'fon_fon_dark.png'), (self.width, self.height))
        self.top = pg.Surface((self.width, self.height / 8))
        self.top.fill((70, 70, 68))
        self.window_scr = pg.Surface((self.width, self.height))
        self.message_text = False
        self.none_button = False
        self.create_background()

    def create_background(self):
        font_head = pg.font.SysFont("comicsans", round(0.059375 * self.width))
        font = pg.font.SysFont("comicsans", round(0.0421875 * self.width))
        font_little_head = pg.font.SysFont("comicsans", round(0.046875 * self.width))
        font_little = pg.font.SysFont("comicsans", round(0.0390625 * self.width))
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
        self.text_length_message1 = font_little.render('Длина ника игрока не может', True, (0, 0, 0))
        self.text_length_message2 = font_little.render('превышать 8 символов', True, (0, 0, 0))
        self.none_button_text1 = font_little.render('Вы не назначили', True, (0, 0, 0))
        self.none_button_text2 = font_little.render('одну из кнопок', True, (0, 0, 0))
        self.background.blit(self.top, (0, 0))
        self.background.blit(music_text, (60 - music_text.get_width() / 2, 350))
        self.background.blit(eff_text, (160 - eff_text.get_width() / 2, 350))
        self.background.blit(control_text, (210 + 190 - control_text.get_width() / 2, 135 - int(control_text.get_height() / 2)))
        self.background.blit(player_nick_text, (220, 87 - int(player_nick_text.get_height() / 2)))
        self.background.blit(forward_text, (220, 175 - int(player_nick_text.get_height() / 2)))
        self.background.blit(back_text, (220, 220 - int(player_nick_text.get_height() / 2)))
        self.background.blit(left_text, (220, 265 - int(player_nick_text.get_height() / 2)))
        self.background.blit(right_text, (220, 310 - int(player_nick_text.get_height() / 2)))
        self.background.blit(shoot_text, (220, 355 - int(player_nick_text.get_height() / 2)))
        self.background.blit(header_text, ((self.width - header_text.get_width()) / 2, self.height * 0.03))
        pg.draw.line(self.background, (57,59,61), (0, 51), (self.width, 51), 3)
        pg.draw.rect(self.background, (47, 48, 48), (10, 60, self.width - 20, self.height - 105), 2)
        pg.draw.rect(self.background, (57,59,61), (0, 0, self.width, self.height), 6)
        pg.draw.line(self.background, (47, 48, 48), (110, 60), (110, 385), 2)
        pg.draw.line(self.background, (47, 48, 48), (210, 60), (210, 385), 2)
        pg.draw.line(self.background, (47, 48, 48), (210, 115), (630, 115), 2)

    def draw(self, win):
        self.window_scr.blit(self.background, (0, 0))
        if self.message_text:
            self.window_scr.blit(self.text_length_message1, (15, 390))
            self.window_scr.blit(self.text_length_message2, (15, 410))
        elif self.none_button:
            self.window_scr.blit(self.none_button_text1, (15, 390))
            self.window_scr.blit(self.none_button_text2, (15, 410))
        self.window_scr.blit(self.music_bar.draw(), (50, 70))
        self.window_scr.blit(self.effects_bar.draw(), (150, 70))
        win.blit(self.window_scr, ((WIDTH - self.width) / 2, (HEIGHT - self.height) / 2 + 20))

    def update(self):
        self.none_button = False
        self.message_text = False
        with open('settings.json') as file:
            data = json.load(file)
            self.first_player_nick = data["player_settings"]["first_player_nick"]
            self.second_player_nick = data["player_settings"]["second_player_nick"]
            self.forward_btn_1 = list(data["player_settings"]["forward_move_btn_1"].values())[0]
            self.forward_btn_1_text = list(data["player_settings"]["forward_move_btn_1"].keys())[0]
            self.back_btn_1 = list(data["player_settings"]["back_move_btn_1"].values())[0]
            self.back_btn_1_text = list(data["player_settings"]["back_move_btn_1"].keys())[0]
            self.left_btn_1 = list(data["player_settings"]["left_move_btn_1"].values())[0]
            self.left_btn_1_text = list(data["player_settings"]["left_move_btn_1"].keys())[0]
            self.right_btn_1 = list(data["player_settings"]["right_move_btn_1"].values())[0]
            self.right_btn_1_text = list(data["player_settings"]["right_move_btn_1"].keys())[0]
            self.shoot_btn_1 = list(data["player_settings"]["shoot_btn_1"].values())[0]
            self.shoot_btn_1_text = list(data["player_settings"]["shoot_btn_1"].keys())[0]
            self.forward_btn_2 = list(data["player_settings"]["forward_move_btn_2"].values())[0]
            self.forward_btn_2_text = list(data["player_settings"]["forward_move_btn_2"].keys())[0]
            self.back_btn_2 = list(data["player_settings"]["back_move_btn_2"].values())[0]
            self.back_btn_2_text = list(data["player_settings"]["back_move_btn_2"].keys())[0]
            self.left_btn_2 = list(data["player_settings"]["left_move_btn_2"].values())[0]
            self.left_btn_2_text = list(data["player_settings"]["left_move_btn_2"].keys())[0]
            self.right_btn_2 = list(data["player_settings"]["right_move_btn_2"].values())[0]
            self.right_btn_2_text = list(data["player_settings"]["right_move_btn_2"].keys())[0]
            self.shoot_btn_2 = list(data["player_settings"]["shoot_btn_2"].values())[0]
            self.shoot_btn_2_text = list(data["player_settings"]["shoot_btn_2"].keys())[0]
            self.music_bar = SliderBar(690, 420, 15, 250, True, value=data["player_settings"]["music"])
            self.effects_bar = SliderBar(790, 420, 15, 250, True, value=data["player_settings"]["effects"])
        self.line_edits_arr = [InputBox(970, 417, 140, 30, text=self.first_player_nick, centering=True),
                          InputBox(1120, 417, 140, 30, text=self.second_player_nick, centering=True),
                          InputBox(970, 505, 140, 30, text=self.forward_btn_1_text, centering=True, usual=False, btn=self.forward_btn_1),
                          InputBox(1120, 505, 140, 30, text=self.forward_btn_2_text, centering=True, usual=False, btn=self.forward_btn_2),
                          InputBox(970, 550, 140, 30, text=self.back_btn_1_text, centering=True, usual=False, btn=self.back_btn_1),
                          InputBox(1120, 550, 140, 30, text=self.back_btn_2_text, centering=True, usual=False, btn=self.back_btn_2),
                          InputBox(970, 595, 140, 30, text=self.left_btn_1_text, centering=True, usual=False, btn=self.left_btn_1),
                          InputBox(1120, 595, 140, 30, text=self.left_btn_2_text, centering=True, usual=False, btn=self.left_btn_2),
                          InputBox(970, 640, 140, 30, text=self.right_btn_1_text, centering=True, usual=False, btn=self.right_btn_1),
                          InputBox(1120, 640, 140, 30, text=self.right_btn_2_text, centering=True, usual=False, btn=self.right_btn_2),
                          InputBox(970, 685, 140, 30, text=self.shoot_btn_1_text, centering=True, usual=False, btn=self.shoot_btn_1),
                          InputBox(1120, 685, 140, 30, text=self.shoot_btn_2_text, centering=True, usual=False, btn=self.shoot_btn_2)]

    def saving(self):
        if len(self.line_edits_arr[0].text) > 9 or len(self.line_edits_arr[1].text) > 9:
            self.message_text = True
            return
        if any([not x.text for x in self.line_edits_arr]):
            self.none_button = True
            return
        with open('settings.json') as f:
            data = json.load(f)
        data['player_settings']['music'] = self.music_bar.value
        data['player_settings']['effects'] = self.effects_bar.value
        data['player_settings']['first_player_nick'] = self.line_edits_arr[0].text
        data['player_settings']['second_player_nick'] = self.line_edits_arr[1].text
        data['player_settings']['forward_move_btn_1'] = {self.line_edits_arr[2].text: self.line_edits_arr[2].btn}
        data['player_settings']['forward_move_btn_2'] = {self.line_edits_arr[3].text: self.line_edits_arr[3].btn}
        data['player_settings']['back_move_btn_1'] = {self.line_edits_arr[4].text: self.line_edits_arr[4].btn}
        data['player_settings']['back_move_btn_2'] = {self.line_edits_arr[5].text: self.line_edits_arr[5].btn}
        data['player_settings']['left_move_btn_1'] = {self.line_edits_arr[6].text: self.line_edits_arr[6].btn}
        data['player_settings']['left_move_btn_2'] = {self.line_edits_arr[7].text: self.line_edits_arr[7].btn}
        data['player_settings']['right_move_btn_1'] = {self.line_edits_arr[8].text: self.line_edits_arr[8].btn}
        data['player_settings']['right_move_btn_2'] = {self.line_edits_arr[9].text: self.line_edits_arr[9].btn}
        data['player_settings']['shoot_btn_1'] = {self.line_edits_arr[10].text: self.line_edits_arr[10].btn}
        data['player_settings']['shoot_btn_2'] = {self.line_edits_arr[11].text: self.line_edits_arr[11].btn}
        with open('settings.json', 'w') as f:
            json.dump(data, f)
        return self.update()


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
        self.window_scr.blit(header_text, ((self.width - header_text.get_width()) / 2, self.height * 0.03))
        self.window_scr.blit(confirm_text, ((self.width - confirm_text.get_width()) / 2, self.height / 4.5))
        pg.draw.line(self.window_scr, (57,59,61), (0, self.height * 0.16), (self.width, self.height * 0.16), 3)
        pg.draw.rect(self.window_scr, (57,59,61), (0, 0, self.width, self.height), 6)
        win.blit(self.window_scr, ((WIDTH - self.width) / 2 + 2, (HEIGHT - self.height) / 2))


class Button:
    def __init__(self, text, x, y, width=616, height=68, size=40, limit=(0, 0)):
        self.text = text
        self.x = x
        self.y = y
        self.limit_x = limit[0]
        self.limit_y = limit[1]
        self.size = size
        self.normal_image = pg.transform.scale(pg.image.load('style/data/system_image/'
                                          'menu_button_normal.png'), (width, height))
        self.hover_image = pg.transform.scale(pg.image.load('style/data/system_image/'
                                         'menu_button_hovered.png'), (width, height))
        self.width, self.height = self.normal_image.get_rect().size

    def draw(self, win):
        x1, y1 = pg.mouse.get_pos()
        font = pg.font.SysFont("comicsans", self.size)
        text = font.render(self.text, True, (255, 255, 255))
        if self.x + self.limit_x <= x1 <= self.x + self.width - self.limit_x and self.y <= y1 <= self.y + self.height:
            win.blit(self.hover_image, (self.x, self.y))
            win.blit(text, (self.x + self.width / 2 - text.get_width() / 2,
                            self.y + self.height / 2 - text.get_height() / 1.65))
        else:
            win.blit(self.normal_image, (self.x, self.y))
            win.blit(text, (self.x + self.width / 2 - text.get_width() / 2,
                            self.y + self.height / 2 - text.get_height() / 1.9))

    def click(self, pos, action, *args):
        x1, y1 = pos[0], pos[1]
        if (self.x + self.limit_x <= x1 <= self.x + self.width - self.limit_x and
                self.y <= y1 <= self.y + self.height) and action:
            click_sound.play()
            if len(args[0]) != 1:
                action(args[0][1:])
            else:
                action()
        else:
            return


def choose_level_screen():
    run = True
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                click_sound.play()
                [btn.click(event.pos, act, arg)
                 for btn, act, arg in lvl_scrn_buttons]
                pg.time.delay(1)
        screen.fill((0, 0, 0))
        screen.blit(lvl_scrn, (0, 0))
        [i[0].draw(screen) for i in lvl_scrn_buttons]
        screen.blit(lvls[0], (1165, 128))
        screen.blit(border, (1100, 54))
        pg.display.flip()
        clock.tick(FPS)


def game_mode_screen():
    run = True
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                click_sound.play()
                [btn.click(event.pos, act, arg)
                 for btn, act, arg in game_mode_buttons]
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
                        speed=1):
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
        clock.tick(FPS)


def first_show():
    time.sleep(1)
    pg.mixer.music.play(loops=-1)
    alpha_change_screen(background, bg_screen, alpha_to=255 // 3)
    st_screen.blit(bg_screen, (0, 0))
    down_drop_text(screen, tanks_battle, tanks_battle_rect)


def start_screen(is_first):
    first_show() if is_first[0] else None
    run = True
    bck_is_drk = False
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
                        [btn.click(event.pos, act, arg)
                         for btn, act, arg in close_win_buttons]
                    if settings_wnd_f:
                        [btn.click(event.pos, act, arg) for btn, act, arg in settings_wnd_btns]
                if settings_wnd_f:
                    [i.handle_event(event) for i in setting_window.line_edits_arr]
            if settings_wnd_f:
                if pg.mouse.get_pressed()[0]:
                    setting_window.music_bar.click(pg.mouse.get_pos())
                    setting_window.effects_bar.click(pg.mouse.get_pos())
                [(i.update(), i.draw(screen)) for i in setting_window.line_edits_arr]
            if exit_wnd_f:
                [i[0].draw(screen) for i in close_win_buttons]
            if settings_wnd_f:
                [i[0].draw(screen) for i in settings_wnd_btns]
            pg.display.flip()
            clock.tick(FPS)
            continue
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                [btn.click(event.pos, act, arg)
                 for btn, act, arg in main_menu_buttons]
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


main_menu_buttons = [[Button('Играть', WIDTH * 0.34, HEIGHT * 0.5, width=int(0.321 * WIDTH), height=int(0.063 * HEIGHT)), game_mode_screen, (False, )],
                     [Button('Настройки', WIDTH * 0.34, HEIGHT * 0.574, width=int(0.321 * WIDTH), height=int(0.063 * HEIGHT)), change_settings_f, (False, )],
                     [Button('Правила', WIDTH * 0.34, HEIGHT * 0.648, width=int(0.321 * WIDTH), height=int(0.063 * HEIGHT)), False, (False, )],
                     [Button('Выход', WIDTH * 0.34, HEIGHT * 0.722, width=int(0.321 * WIDTH), height=int(0.063 * HEIGHT)), change_exit_f, (False, )]]


close_win_buttons = [[Button('Выйти', int(WIDTH / 2 - 0.1 * WIDTH),
                             int(HEIGHT / 2 + 0.15 * HEIGHT / 4),
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=20), terminate, (False, )],
                     [Button('Отмена', int(WIDTH / 2),
                             int(HEIGHT / 2 + 0.15 * HEIGHT / 4),
                             width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03),
                             size=20), change_exit_f, (False, )]]


exit_window = ConfirmWindow('Подтвреждение', 'Вы действительно хотите выйти?')
setting_window = SettingsWindow()


game_mode_buttons = [[Button('Кампания', WIDTH * 0.34, HEIGHT * 0.426), choose_level_screen, (False, )],
                     [Button('Играть', WIDTH * 0.34, HEIGHT * 0.5), False, (False, )],
                     [Button('Игра с другом', WIDTH * 0.34, HEIGHT * 0.574), False, (False, )],
                     [Button('Онлайн', WIDTH * 0.34, HEIGHT * 0.648), False, (False, )],
                     [Button('Назад', WIDTH * 0.34, HEIGHT * 0.722), start_screen, (False, False)]]


settings_wnd_btns = [[Button('Сохранить', 944, 737, width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03), size=20, limit=(20, 0)), setting_window.saving, (False, )],
                     [Button('Назад', 1094, 737, width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03), size=20, limit=(20, 0)), change_settings_f, (False, )],
                     [Button('По умолчанию', 794, 737, width=int(WIDTH * 0.1), height=int(HEIGHT * 0.03), size=20, limit=(20, 0)), default_settings, (False, )]]


lvl_scrn_buttons = [[Button('Уровень 1', -50, HEIGHT * 0.05, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.11, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.17, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.23, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.29, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.35, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.41, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.47, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.53, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.59, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.65, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', -50, HEIGHT * 0.71, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.05, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.11, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.17, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.23, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.29, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.35, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.41, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.47, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.53, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.59, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.65, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Уровень 1', WIDTH * 0.1822916, HEIGHT * 0.71, width=int(WIDTH * 0.25), height=int(HEIGHT * 0.05), limit=(90, 0)), False, (False,)],
                    [Button('Назад', 85, HEIGHT * 0.85), game_mode_screen, (False,)],
                    [Button('Играть', 1175, HEIGHT * 0.85), False, (False,)]]


lvls = [pg.transform.scale(pg.image.load('style/data/system_image/lvl.jpg'), (623, 608)),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),
        pg.image.load('style/data/system_image/lvl.jpg'),]



def main():
    running = True
    type_game, level, select_screen = start_screen((True, ))
    print(type_game, level)
    while running:
        screen.blit(background, (0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.blit(select_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)
    pg.quit()


if __name__ == '__main__':
    main()
