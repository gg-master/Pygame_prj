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
    all_track = {
        'shoot_player': 'shoot_sound\\shoot_1.wav',
        'shoot_bot': 'shoot_sound\\shoot_2.wav',
        'exp1': 'explosion_sound\\explosion1.wav',
        'exp2': 'explosion_sound\\explosion2.wav',
        'exp3': 'explosion_sound\\explosion3.wav',
        'exp4': 'explosion_sound\\explosion4.wav',
        'exp5': 'explosion_sound\\explosion5.wav',
        'exp6': 'explosion_sound\\explosion6.wav',
        'exp7': 'explosion_sound\\explosion7.wav',
        'hit1': 'hit_sound\\hit_bullet.wav',
        'hit2': 'hit_sound\\hit_bullet2.wav',
        'hit3': 'hit_sound\\hit_bullet3.wav',
        'hit4': 'hit_sound\\hit_bullet4.wav',
        'ric1': 'hit_sound\\ricochet.wav',
        'ric2': 'hit_sound\\ricochet2.wav',
        'select1': 'select_sound\\select1.wav',
        'select2': 'select_sound\\select2.wav',
        'select3': 'select_sound\\select3.wav',
        'select4': 'select_sound\\select4.wav',
        'select5': 'select_sound\\select5.wav',
        'move_s1': 'tanks_sound\\move_sound.wav',
        'move_s2': 'tanks_sound\\move_sound2.mp3',
        'turning_turret': 'tanks_sound\\turning_turret.wav',
        'waiting': 'tanks_sound\\waiting_in_tank_low.wav',
        'grenade': 'bonus_sound\\grenade.wav',
        'shovel': 'bonus_sound\\shovel.wav',
    }

    def __init__(self, settings):
        self.sound_list = {}
        self.music_list = {}
        self.active_sound = {}  # 'player1': ['move']
        self.volume_music = settings['music']
        self.volume_effects = settings['effects']
        self.load_sounds()

    def load_sounds(self):
        if os.getcwd().split('\\')[-1] == 'modules':
            os.chdir('..')
        for name in self.all_track.keys():
            self.sound_list[name] = pygame.mixer.Sound(
                os.path.join(SOUND_DIR, self.all_track[name]))
            self.sound_list[name].set_volume(self.volume_effects / 100)

    def analyze_active_sound_list(self, track_list):
        white_list = {}
        for tr in track_list:
            if isinstance(tr, dict):
                key = list(tr.keys())[0]
                if key in white_list:
                    white_list[key].append(tr[key])
                else:
                    white_list[key] = [tr[key]]

        for k_act_s in list(self.active_sound.keys()):
            if k_act_s in self.active_sound:
                if k_act_s not in white_list:
                    # Если ключа нет в белом списке,
                    # то выключаем все звуки для этого ключа из списка активных
                    for i in self.active_sound[k_act_s]:
                        self.sound_list[i].fadeout(200)
                    del self.active_sound[k_act_s]
                else:
                    to_del = []
                    for i in self.active_sound[k_act_s]:
                        if i not in white_list[k_act_s]:
                            self.sound_list[i].fadeout(200)
                            to_del.append(self.active_sound[k_act_s].index(i))
                    for index in to_del:
                        del self.active_sound[k_act_s][index]

    def play_list(self, track_list):
        for name_track in track_list:
            if isinstance(name_track, dict):
                key = list(name_track.keys())[0]
                n_m = name_track[key]
                if key in self.active_sound:
                    if n_m not in self.active_sound[key]:
                        self.sound_list[n_m].play()
                        self.active_sound[key].append(n_m)
                else:
                    self.sound_list[n_m].play()
                    self.active_sound[key] = [n_m]

            elif name_track in self.sound_list:
                self.sound_list[name_track].play()
            else:
                print('track not found')

    def update(self, game):
        track_list = game.get_track_list()
        self.play_list(track_list)
        self.analyze_active_sound_list(track_list)
        # print(self.active_sound)
        #  TODO при постановке игры на пазу, необходимо
        #   всю музыку поставить на паузу


class Client:
    def __init__(self, count_players, type_game, screen):
        self.settings = load_settings()
        self.pl_settings = self.settings['player_settings']

        self.music_player = MusicPlayer(self.pl_settings)
        self.game = Game(count_players, type_game, screen)

    def update(self, *args):
        keystate = self.get_key_state()
        self.game.update(*args, keystate=keystate)
        self.music_player.update(self.game) if not args else ''

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
