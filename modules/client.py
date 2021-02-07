import os
import pygame
from game import Game
from default_funcs import load_settings

WIDTH, HEIGHT = 950, 750
FPS = 60

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
monitor_size = [pygame.display.Info().current_w,
                pygame.display.Info().current_h]
background = pygame.Surface((WIDTH, HEIGHT))

SOUND_DIR = 'data\\music\\'


class MusicPlayer:
    music = {
        'shoot_player': 'shoot_1.wav',
        'shoot_bot': 'shoot_2.wav',
        'explosion_bullet_1': '',
        'explosion_bullet_2': '',
        'explosion_tank_1': '',
        'explosion_tank_2': ''
    }

    def __init__(self, settings):
        self.volume_music = settings['music']
        self.volume_effects = settings['effects']
        self.load_sounds()

    def load_sounds(self):
        if os.getcwd().split('\\')[-1] == 'modules':
            os.chdir('..')
        for name in self.music:
            if not self.music[name]:
                continue
            self.music[name] = pygame.mixer.Sound(
                os.path.join(SOUND_DIR, self.music[name]))
            self.music[name].set_volume(self.volume_effects / 100)

    def play_list(self, track_list):
        for name_track in track_list:
            if name_track in self.music:
                self.music[name_track].play()
            else:
                print('track not found')


class Client:
    def __init__(self, count_players, type_game, screen):
        self.settings = load_settings()
        self.pl_settings = self.settings['player_settings']

        self.music_player = MusicPlayer(self.pl_settings)
        self.game = Game(count_players, type_game, screen)

    def update(self, *args):
        keystate = self.get_key_state()
        self.game.update(*args, keystate=keystate)
        self.music_player.play_list(self.game.get_track_list())

    def render(self):
        self.game.render()

    def get_key_state(self):
        keystate = pygame.key.get_pressed()
        arr_state = {1: [], 2: []}
        for name_button in ['back_move_btn_1', 'back_move_btn_2',
                            'forward_move_btn_1', 'forward_move_btn_2',
                            'left_move_btn_1', 'left_move_btn_2',
                            'right_move_btn_1', 'right_move_btn_2',
                            'shoot_btn_1', 'shoot_btn_2']:
            name = self.pl_settings[name_button]
            if keystate[pygame.key.key_code(name)]:
                action, player = name_button.split('_')[0],\
                                 int(name_button.split('_')[-1])
                arr_state[player].append(action)
        return arr_state


fullscreen = False


if __name__ == '__main__':
    clock = pygame.time.Clock()
    running = True
    client = Client(2, 1, screen)
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h),
                                                     pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(monitor_size,
                                                         pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(
                            (screen.get_width(), screen.get_height()),
                            pygame.RESIZABLE)
            client.update(event)
        client.update()
        client.render()

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
