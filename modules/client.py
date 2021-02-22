import os
import pygame
from game import Game
from default_funcs import load_settings, load_image

WIDTH, HEIGHT = 950, 750
FPS = 60

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(35)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
monitor_size = [pygame.display.Info().current_w,
                pygame.display.Info().current_h]
background = pygame.Surface((WIDTH, HEIGHT))

SOUND_DIR = 'data\\music\\'


class MusicPlayer:
    all_sound = {
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
        'hit5': 'hit_sound\\hit_bullet5.wav',
        'hit6': 'hit_sound\\hit_bullet4low.wav',
        'hit7': 'hit_sound\\hit_bullet3low.wav',
        'ric1': 'hit_sound\\ricochet.wav',
        'ric2': 'hit_sound\\ricochet2.wav',
        'ric1b': 'hit_sound\\ricochet_b.wav',
        'ric2b': 'hit_sound\\ricochet2_b.wav',
        'select1': 'select_sound\\select1.wav',
        'select2': 'select_sound\\select2.wav',
        'select3': 'select_sound\\select3.wav',
        'select4': 'select_sound\\select4.wav',
        'select5': 'select_sound\\select5.wav',
        'move_s1': 'tanks_sound\\move_sound.wav',
        'move_s2': 'tanks_sound\\move_sound2.wav',
        'turning_turret': 'tanks_sound\\turning_turret.wav',
        'waiting': 'tanks_sound\\waiting_in_tank.wav',
        'grenade': 'bonus_sound\\grenade.wav',
        'shovel': 'bonus_sound\\shovel.wav'
    }
    all_music = {
        'won': 'music/skirmish_won.mp3',
        'lost': 'music/skirmish_lost.mp3',
        'bg1': 'music/skirmish_background_01.mp3',
        'bg2': 'music/skirmish_background_02.mp3',
        'bg3': 'music/skirmish_progress.mp3'
    }

    def __init__(self, settings):
        self.track_list = {}
        self.active_sound = {}  # 'player1': ['move']

        self.volume_music = settings['music']
        self.volume_effects = settings['effects']

        self.music_channel = pygame.mixer.Channel(pygame.mixer.
                                                  get_num_channels() - 1)
        self.load_tracks()
        self.play_music('bg1')
        self.was_pause = False

    def load_tracks(self):
        if os.getcwd().split('\\')[-1] == 'modules':
            os.chdir('..')
        for name in self.all_sound.keys():
            self.track_list[name] = pygame.mixer.Sound(
                os.path.join(SOUND_DIR, self.all_sound[name]))
            self.track_list[name].set_volume(self.volume_effects / 100)
        for name in self.all_music.keys():
            if name in self.track_list:
                print('track already exists')
            self.track_list[name] = pygame.mixer.Sound(
                os.path.join(SOUND_DIR, self.all_music[name]))
            self.track_list[name].set_volume(self.volume_music / 2 / 100)

    def play_music(self, name):
        if name not in self.track_list:
            print('music not found')
            return
        self.music_channel.fadeout(600)
        self.music_channel.play(self.track_list[name], -1,
                                fade_ms=600 if name not in ['lost'] else 0)

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
                        self.track_list[i].fadeout(200)
                    del self.active_sound[k_act_s]
                else:
                    for i in self.active_sound[k_act_s]:
                        if i not in white_list[k_act_s]:
                            self.track_list[i].fadeout(200)
                            del self.active_sound[k_act_s][
                                self.active_sound[k_act_s].index(i)]

    def play_list(self, track_list):
        for name_track in track_list:
            if isinstance(name_track, dict):
                key = list(name_track.keys())[0]
                n_m = name_track[key]
                if key == 'change_music':
                    self.play_music(n_m)
                    continue
                if key in self.active_sound:
                    if n_m not in self.active_sound[key]:
                        self.track_list[n_m].play(-1)
                        self.active_sound[key].append(n_m)
                else:
                    self.track_list[n_m].play(-1)
                    self.active_sound[key] = [n_m]

            elif name_track in self.track_list:
                self.track_list[name_track].play()
                # pass
            else:
                print('sound not found')

    def stop_all(self):
        pygame.mixer.stop()

    def update(self, game):
        if game.is_pause:
            self.was_pause = True
            pygame.mixer.pause()
            pygame.mixer.music.pause()
        elif not game.is_pause and self.was_pause:
            self.was_pause = False
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()
        track_list = game.get_track_list()
        self.play_list(track_list)
        self.analyze_active_sound_list(track_list)


class Client:
    def __init__(self, type_game, number_level, screen_surf):
        self.settings = load_settings()
        self.pl_settings = self.settings['player_settings']
        self.type_game = type_game
        self.number_level = number_level
        self.screen = screen_surf
        self.is_exit = False

        self.ld_image = pygame.transform.scale(
            load_image('fon/loading.png'), self.screen.get_size())
        self.music_player = self.game = None
        self.create_new_game(self.type_game,
                             self.number_level, self.screen)

    def create_new_game(self, count_players, type_game, sc):
        self.screen.blit(self.ld_image, (0, 0))
        pygame.display.flip()
        if self.music_player is not None:
            self.music_player.stop_all()
        self.music_player = MusicPlayer(self.pl_settings)
        self.game = Game(count_players, type_game, sc)

    def update(self, *args):
        if self.game.feedback is not None:
            feedback = self.game.feedback
            if feedback == 'continue':
                self.create_new_game(self.type_game,
                                     self.number_level + 1, self.screen)
            elif feedback == 'restart':
                self.create_new_game(self.type_game,
                                     self.number_level, self.screen)
            elif feedback == 'exit':
                self.is_exit = True
        mouse_pos = pygame.mouse.get_pos()
        keystate = self.get_key_state()
        self.game.update(*args, keystate=keystate,
                         mouse_state=[mouse_pos, pygame.mouse.get_pressed(3)])
        self.music_player.update(self.game) if not args else ''

    def render(self):
        mouse_pos = pygame.mouse.get_pos()
        self.game.render(mouse_pos=mouse_pos)

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
        if client.is_exit:
            print('Выход в меню')
            break
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
