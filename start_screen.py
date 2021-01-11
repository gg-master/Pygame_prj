from constants import *
from globals import *
from default_funcs import *
import pygame as pg
import pygame_gui
import sys
import os
import time

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
background = pg.Surface((WIDTH, HEIGHT))
background.fill((0, 0, 0, 0))
pg.display.set_caption(CAPTION)
clock = pg.time.Clock()
maps = ['']


def level_selection_screen():
    nw_screen = pg.Surface(screen.get_size())
    count = 1  # счетчик выбора уровня

    font_mt = pg.font.Font(None, 50)
    font_tips = pg.font.Font(None, 20)

    text_continue = font_tips.render(
        'Продолжить', True, (255, 255, 255))
    text_celect = font_tips.render(
        'Выбрать', True, (255, 255, 255))

    manager = pygame_gui.ui_manager.UIManager((WIDTH, HEIGHT),
                                              'style/level_choose.json')
    # TODO вывести создание кнопок в отдельную функцию. Сделать грамотно
    w, h = 30, 30
    enter = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect((WIDTH - 90, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='enter')
    arrow1 = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect((WIDTH - 90 - 130, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='arrow1')
    arrow2 = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect((WIDTH - 90 - 130 - w, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='arrow2')
    escape = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect((WIDTH - 90 - 260, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='escape')
    # TODO Дописать кнопку escape
    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    if count > 1:
                        count -= 1
                if event.key == pg.K_UP:
                    if count < len(maps):
                        count += 1
                if event.key == pg.K_KP_ENTER:
                    return count, nw_screen
                if event.key == pg.K_ESCAPE:
                    return
            if event.type == pg.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == arrow1:
                        if count > 1:
                            count -= 1
                    if event.ui_element == arrow2:
                        if count < len(maps):
                            count += 1
                    if event.ui_element == enter:
                        return count, nw_screen
                    if event.ui_element == escape:
                        return
            manager.process_events(event)
        manager.update(time_delta)

        nw_screen.fill((115, 117, 115))
        text = font_mt.render(f'Уровень {count}', True,
                              pg.color.Color('white'))
        nw_screen.blit(text, (
            WIDTH // 2 - text.get_rect().width // 2,
            HEIGHT // 2 - text.get_rect().height // 2))
        nw_screen.blit(text_continue, (
            WIDTH - text_continue.get_rect().width - 95,
            HEIGHT - text_continue.get_rect().height - 58))
        nw_screen.blit(text_celect, (
            WIDTH - text_celect.get_rect().width - 255,
            HEIGHT - text_celect.get_rect().height - 58))

        manager.draw_ui(nw_screen)

        screen.blit(nw_screen, (0, 0))
        pg.display.flip()
        screen.fill(pg.color.Color('black'))
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
    y_to = 80
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
        surf.blit(image, (WIDTH // 2 - rect.width // 2, y))
        screen.blit(surf, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def create_button(info, manager):
    button = pygame_gui.elements.UIButton(
        relative_rect=pg.Rect((info[0], info[1]), (info[2], info[3])),
        text=info[4],
        manager=manager,
        object_id=info[5])
    return button


def start_screen():
    time.sleep(1)
    manager = pygame_gui.ui_manager.UIManager((WIDTH, HEIGHT), 'style/menu.json')
    fon = pg.transform.scale(load_image('fon5.png'), (WIDTH, HEIGHT))
    st_screen = pg.Surface(screen.get_size())
    bg_screen = pg.Surface(screen.get_size())
    bg_screen.blit(fon, (0, 0))
    alpha_change_screen(background, bg_screen, alpha_to=255 // 3)
    st_screen.blit(bg_screen, (0, 0))
    tanks_battle = load_image(GAME_HEADER_PATH)
    tanks_battle_rect = tanks_battle.get_rect()
    down_drop_text(screen, tanks_battle, tanks_battle_rect)
    play, settings, rules, escape = [create_button(i, manager) for i
                                     in MENU_BUTTONS]
    run = True
    while run:
        time_delta = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                call_confirm_dialog(manager)
            if event.type == pg.USEREVENT:
                if event.user_type == \
                        pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    run = False
                    terminate()
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play:
                        rez = level_selection_screen()
                        print(rez)
                        if rez is not None:
                            return '1', rez[0], rez[1]
                    if event.ui_element == rules:
                        print('rules')
            manager.process_events(event)
        screen.fill(pg.color.Color('black'))
        st_screen.fill((0, 0, 0))
        manager.update(time_delta)
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(tanks_battle, (
            WIDTH // 2 - tanks_battle_rect.width // 2, 80))
        manager.draw_ui(st_screen)
        screen.blit(st_screen, (0, 0))
        pg.display.flip()
        clock.tick(FPS)


def main():
    running = True
    type_game, level, select_screen = start_screen()
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
