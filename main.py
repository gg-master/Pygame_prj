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

manager = pygame_gui.ui_manager.UIManager((WIDTH, HEIGHT))


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


class ChoiceScreen:
    def __init__(self):
        pass


def choice_screen():
    pass
    # s_screen = pygame.Surface(screen.get_size())
    # s_screen.set_alpha(255 // 3)
    # fon = pygame.transform.scale(load_image('screen.png'), (WIDTH, HEIGHT))
    # s_screen.blit(fon, (0, 0))
    #
    # tanks_battle = load_image('TanksBattle.png')
    #
    #
    # clock = pygame.time.Clock()
    #
    #
    #
    # while True:
    #
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             terminate()
    #         if event.type == pygame.USEREVENT:
    #             if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
    #                 if event.ui_element == button1:
    #                     print('Button1.pressed')
    #         manager.process_events(event)
    #     manager.update(time_delta)
    #     screen.fill(pygame.color.Color('black'))
    #     screen.blit(s_screen, (0, 0))
    #     screen.blit(tanks_battle, (WIDTH // 4, 50))
    #     manager.draw_ui(screen)
    #     pygame.display.flip()
    #     clock.tick(FPS)


def start_screen():
    time.sleep(1)
    clock = pygame.time.Clock()
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))

    st_screen = pygame.Surface(screen.get_size())

    bg_screen = pygame.Surface(screen.get_size())
    bg_screen.blit(fon, (0, 0))

    alpha_change_screen(background, bg_screen, alpha_to=255//3)

    tanks_battle = load_image('TanksBattle.png')
    tanks_battle_rect = tanks_battle.get_rect()

    st_screen.blit(bg_screen, (0, 0))
    down_drop_text(st_screen, tanks_battle, tanks_battle_rect)

    w, h = 150, 35
    button1 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2),
                                  (w, h)),
        text='1Player',
        manager=manager
    )
    while True:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    alpha_change_screen(st_screen, background, speed=25)
                    return
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button1:
                        print('Button1.pressed')
            manager.process_events(event)
        screen.fill(pygame.color.Color('black'))
        st_screen.fill((0, 0, 0))

        manager.update(time_delta)
        st_screen.blit(bg_screen, (0, 0))
        st_screen.blit(tanks_battle, (WIDTH // 2 - tanks_battle_rect.width // 2, 80))
        manager.draw_ui(st_screen)

        screen.blit(st_screen, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def down_drop_text(surf, image, rect):
    clock = pygame.time.Clock()
    y = -rect.height
    y_to = 80
    orig_surf = surf.copy()
    while y < y_to:
        y += 4
        surf.blit(orig_surf, (0, 0))
        surf.blit(image, (WIDTH // 2 - rect.width // 2, y))

        screen.blit(surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def alpha_change_screen(surf_from, surf_to, alpha_from=0, alpha_to=255, speed=1):
    surf_from.set_alpha(255)
    surf_to.set_alpha(0)

    clock = pygame.time.Clock()
    alpha = 255
    alpha2 = 0

    while alpha2 < alpha_to and alpha > alpha_from:
        # Reduce alpha each frame.
        alpha2 += speed
        alpha2 = min(255, alpha2)

        alpha -= speed
        alpha = max(0, alpha)

        surf_from.set_alpha(alpha)
        surf_to.set_alpha(alpha2)
        screen.blit(surf_from, (0, 0))
        screen.blit(surf_to, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)


def main():
    clock = pygame.time.Clock()
    running = True

    start_screen()
    choice_screen()

    while running:
        # screen.fill(pygame.Color('white'))
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
