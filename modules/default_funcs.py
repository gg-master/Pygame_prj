import pygame as pg
import json
import os
import sys


SETTINGS_PATH = 'settings/settings.json'


def load_settings():
    if os.getcwd().split('\\')[-1] == 'modules':
        os.chdir('..')
    with open(SETTINGS_PATH) as settings_file:
        return json.load(settings_file)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pg.quit()
    sys.exit()
