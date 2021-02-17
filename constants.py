# 'NS'(Not Stated) - те значения, которые еще пока не указаны
WIDTH = 1920
HEIGHT = 1080
FPS = 60
CAPTION = 'Tanks Battle'
MAIN_TANK_1_SKIN_PATH = 'путь к скину главного танка'
MAIN_TANK_2_SKIN_PATH = 'путь к скину второго главного танка'
BOT_LITE_TANK_SKIN_PATH = 'путь к скину легкого танка'
BOT_MEDIUM_TANK_SKIN_PATH = 'путь к скину среднего такнка'
BOT_HEAVY_TANK_SKIN_PATH = 'путь к скину тяжелого танка'
MAIN_MENU_MUSIC_PATH = r'C:\Users\olrol\PycharmProjects\Pygame_prj\data\music\main_theme.mp3'
CLICK_BUTTON_SOUND_PATH = r'C:\Users\olrol\PycharmProjects\Pygame_prj\data\sounds\click.wav'
DEFAULT_MAIN_TANK_SKIN_PATH = 'путь к стандартному скину танка'
RED_MAIN_TANK_SKIN_PATH = 'путь к красному скину танка'
GREEN_MAIN_TANK_SKIN_PATH = 'путь к зеленому скину танка'
DARK_GREY_MAIN_TANK_SKIN_PATH = 'путь к темно-серому скину танка'
GAME_HEADER_PATH = 'TanksBattle.png'
W_MENU, H_MENU, SPACE_MENU = 360, 60, 20
W_BUTTON_MENU, H_BUTTON_MENU = WIDTH // 2 - W_MENU // 2,\
                               HEIGHT // 2 - H_MENU // 2
MENU_BUTTONS = [[W_BUTTON_MENU, H_BUTTON_MENU, W_MENU, H_MENU, 'Играть',
                 'menu_play'],
                [W_BUTTON_MENU, H_BUTTON_MENU + H_MENU + SPACE_MENU,
                 W_MENU, H_MENU, 'Настройки', 'settings'],
                [W_BUTTON_MENU, H_BUTTON_MENU + (H_MENU + SPACE_MENU) *
                 2, W_MENU, H_MENU, 'Правила', 'rules'],
                [W_BUTTON_MENU, H_BUTTON_MENU + (H_MENU + SPACE_MENU) *
                 3, W_MENU, H_MENU, 'Выход', 'quit']]
print(W_BUTTON_MENU, H_BUTTON_MENU, W_MENU, H_MENU)
