import pygame
import pygame_gui
import sys
import os
import time

WIDTH, HEIGHT = 950, 750
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

background = pygame.Surface((WIDTH, HEIGHT))
background.fill((0, 0, 0, 0))

pygame.display.set_caption('Tanks Battle')

maps = ['']

path_for_sys_img = 'system_image/'


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


def terminate():
    pygame.quit()
    sys.exit()


def down_drop_text(surf, image, rect):
    # Функция, которая опускает картинку с текстом из-за
    # границы экрана в необходимое место
    clock = pygame.time.Clock()
    y = -rect.height
    y_to = 80
    orig_surf = surf.copy()
    while y < y_to:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER:
                    return
        y += 4
        surf.blit(orig_surf, (0, 0))
        surf.blit(image, (WIDTH // 2 - rect.width // 2, y))

        screen.blit(surf, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def alpha_change_screen(surf_from, surf_to, alpha_from=0,
                        alpha_to=255, speed=1):
    # Функция, меняющаяя местами окна, путем мзенения альфа канала
    # speed - подразумевает под собой скорость изменеия альфа каналов
    surf_from.set_alpha(255)
    surf_to.set_alpha(0)

    clock = pygame.time.Clock()
    alpha = 255
    alpha2 = 0

    while alpha2 < alpha_to and alpha > alpha_from:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER:
                    surf_to.set_alpha(alpha_to)
                    screen.blit(surf_to, (0, 0))
                    return
        # Reduce alpha each frame.
        alpha2 += speed
        alpha2 = min(255, alpha2)

        alpha -= speed
        alpha = max(0, alpha)

        # surf_from.set_alpha(alpha)
        surf_to.set_alpha(alpha2)
        screen.blit(surf_from, (0, 0))
        screen.blit(surf_to, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)


def scale_sys_image(image):
    # scale_W_to = 50
    # img_rect = image.get_rect()
    # img = pygame.transform.scale(image, ())
    return image


def level_selection_screen():
    clock = pygame.time.Clock()
    nw_screen = pygame.Surface(screen.get_size())
    count = 1  # счетчик выбора уровня

    font_mt = pygame.font.Font(None, 50)
    font_tips = pygame.font.Font(None, 20)

    text_continue = font_tips.render(
        'Продолжить', True, (255, 255, 255))
    text_celect = font_tips.render(
        'Выбрать', True, (255, 255, 255))

    manager = pygame_gui.ui_manager.UIManager((WIDTH, HEIGHT),
                                              'style/level_choose.json')
    # TODO вывести создание кнопок в отдельную функцию. Сделать грамотно
    w, h = 30, 30
    enter = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 90, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='enter')
    arrow1 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 90 - 130, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='arrow1')
    arrow2 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 90 - 130 - w, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='arrow2')
    escape = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 90 - 260, HEIGHT - 80),
                                  (w, h)),
        text='',
        manager=manager,
        object_id='escape')
    # TODO Дописать кнопку escape
    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if count > 1:
                        count -= 1
                if event.key == pygame.K_UP:
                    if count < len(maps):
                        count += 1
                if event.key == pygame.K_KP_ENTER:
                    return count, nw_screen
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.USEREVENT:
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
                              pygame.color.Color('white'))
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
        pygame.display.flip()
        screen.fill(pygame.color.Color('black'))
        clock.tick(FPS)


def start_screen():
    time.sleep(1)
    clock = pygame.time.Clock()
    manager = pygame_gui.ui_manager.UIManager((WIDTH, HEIGHT))

    fon = pygame.transform.scale(load_image('fon\\fon3.png'), (WIDTH, HEIGHT))

    # Создаем несколько поверхностей, для отрисовки чуть
    # более темного фона и основных кнопок
    st_screen = pygame.Surface(screen.get_size())
    bg_screen = pygame.Surface(screen.get_size())
    # Отрисоввываем на заднюю поверхность фоновую картинку
    bg_screen.blit(fon, (0, 0))

    # Анимация плавного появления окна
    # Реализовано через изменение альфа каналов
    alpha_change_screen(background, bg_screen, alpha_to=int(255/3))
    # Отрисовываем на основную поверхность задний фон
    st_screen.blit(bg_screen, (0, 0))

    # Создаем картинку с надписью названия игры
    tanks_battle = load_image('TanksBattle.png')
    tanks_battle_rect = tanks_battle.get_rect()
    # Анимация плавного появления текста из-за верхней границы экрана
    down_drop_text(screen, tanks_battle, tanks_battle_rect)
    # Создание кнопок на экране
    # TODO оптимизировать создание кнопок
    game_for_one, game_for_two, game_for_two_online, settings, rules \
        = create_buttons(manager)

    run = True
    while run:
        # Установка таймера для  корректной работы pygame_gui менеджера
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Перед закрытием окна узаем у пользователя,
                # действительно ли он хочет закрыть окно
                conf_dialog = pygame_gui.windows.UIConfirmationDialog(
                    rect=pygame.Rect(
                        (WIDTH // 2 - 150, HEIGHT // 2 - 100), (300, 200)),
                    manager=manager,
                    window_title='Подтверждение',
                    action_long_desc='Вы уверены, что хотите выйти?',
                    action_short_name='Ok',
                    blocking=True
                )
            if event.type == pygame.USEREVENT:
                # Узнаем были ли нажаты какие-либо кнопки на экране
                if event.user_type == \
                        pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    run = False
                    terminate()
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == game_for_one:
                        rez = level_selection_screen()
                        print(rez)
                        if rez is not None:
                            return '1', rez[0], rez[1]
                    if event.ui_element == rules:
                        print('rules')
            manager.process_events(event)

        # Обновление экрана
        screen.fill(pygame.color.Color('black'))
        st_screen.fill((0, 0, 0))

        manager.update(time_delta)
        # Отрисовка всех элементов последовательно
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(tanks_battle, (
            WIDTH // 2 - tanks_battle_rect.width // 2, 80))

        manager.draw_ui(st_screen)

        screen.blit(st_screen, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def create_buttons(manager):
    w, h = 300, 45
    space = 15
    b1 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2),
                                  (w, h)),
        text='Кампания для одного игрока',
        manager=manager
    )
    b2 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(
            (WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2 + h + space),
            (w, h)),
        text='Кампания для двух игрков',
        manager=manager
    )
    b3 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(
            (WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2 + (h + space) * 2),
            (w, h)),
        text='Кампания для двух игроков по сети',
        manager=manager
    )
    b4 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(
            (WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2 + (h + space) * 3),
            (w, h)),
        text='Настройки',
        manager=manager
    )
    b5 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(
            (WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2 + (h + space) * 4),
            (w, h)),
        text='Правила',
        manager=manager
    )
    return b1, b2, b3, b4, b5


def main():
    clock = pygame.time.Clock()
    running = True

    # Фунция, с главным игровым циклом.
    # Сначала закружается стартовый экран с выбором типа игры,
    # ознакомления с правилами и настрокой игры(громкости, и тд)

    # Далее выбираем уровень игры. Далее запускаем игровой цикл,
    # в зависимости от выбранного типа игры
    type_game, level, select_screen = start_screen()
    from modules import game
    # После получения типа игры и уровня,
    # мы должны в течении нескольких секунд
    # показывать экран с выбором уровня и проигрывать музыку
    # TODO делать счетчик на "зависание" экрана
    #  с выбором уровня. Паралельно включив музыку
    print(type_game, level)
    game = game.Game(int(type_game), int(level))
    while running:
        # screen.fill(pygame.Color('white'))
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.update(event)
        game.render()
        game.update()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
