import pytmx
import pygame

MAPDIR = 'data\\maps\\'
WORLDIMG_DIR = 'data\\world\\'
WIDTH, HEIGHT = 950, 750
MAP_SIZE = 650
FPS = 60

TILE_FOR_PLAYERS = 16
TILE_FOR_MOBS = 17

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, layer, tile_size, player):
        super().__init__()
        self.coords = [x, y]
        self.layer = layer
        self.TILE_SIZE = tile_size
        self.velocity = 4


class Map:
    def __init__(self, path, map_size):
        self.map = pytmx.load_pygame(path)
        self.TILE_SIZE = map_size // self.map.width
        self.width = self.map.width
        self.height = self.map.height
        self.koeff = self.map.tilewidth / self.TILE_SIZE

    def get_tile_image(self, x, y, layer):
        image = self.map.get_tile_image(x, y, layer)
        if image is not None:
            image = pygame.transform.scale(image,
                                           (self.TILE_SIZE, self.TILE_SIZE))
            return image

    def get_objects(self, name):
        return self.map.layernames[name]

    def get_tile_id(self, gid):
        return self.map.tiledgidmap[gid]

    def get_tiled_by_id(self, id):
        return list(map(lambda x: x, self.map.get_tile_locations_by_gid(
            list(self.map.tiledgidmap.values()).index(id) + 1)))


class Wall(pygame.sprite.Sprite):
    type_wall = {
        3: 'wall_RT.png',
        4: 'wall_RD.png',
        5: 'wall_LT.png',
        6: 'wall_LD.png',
        7: 'wall_T.png',
        8: 'wall_R.png',
        9: 'wall_L.png',
        10: 'wall_D.png',
        11: 'wall_1.png'
    }

    def __init__(self, x, y, id, tile_size):
        super().__init__()
        self.image = pygame.image.load(f'{WORLDIMG_DIR}{self.type_wall[id]}')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.tile_size = tile_size

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y


class Game:
    def __init__(self, type_game, number_level):
        self.map = Map(f'{MAPDIR}map{number_level}.tmx', MAP_SIZE)
        self.map_object = self.map.map
        self.TILE_SIZE = self.map.TILE_SIZE

        self.player1 = None
        self.player2 = None
        self.all_sprites = pygame.sprite.Group()
        self.mobs_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()

        # print(self.map.get_objects('eagle')[0].image)
        for i in self.map.get_objects('walls'):
            x, y = i.x / self.map.koeff + 50, i.y / self.map.koeff + 50
            wall = Wall(x, y, self.map.get_tile_id(i.gid), self.TILE_SIZE)
            wall.add(self.all_sprites, self.wall_group)

        self.TILES_FOR_PLAYERS = self.map.get_tiled_by_id(TILE_FOR_PLAYERS)

        self.TILES_FOR_MOBS = self.map.get_tiled_by_id(TILE_FOR_MOBS)

        if type_game == 1:
            self.player1 = Player(*self.TILES_FOR_PLAYERS[0],
                                  self.TILE_SIZE, player=0)
            self.player1.add(self.player_group, self.all_sprites)

        elif type_game == 2:
            self.player1 = Player(*self.TILES_FOR_PLAYERS[0],
                                  self.TILE_SIZE, player=0)
            self.player2 = Player(*self.TILES_FOR_PLAYERS[1],
                                  self.TILE_SIZE, player=1)

            self.player1.add(self.player_group, self.all_sprites)
            self.player2.add(self.player_group, self.all_sprites)
        elif type_game == 3:
            raise Exception('Онлайн еще не готов')

    def render(self):
        # Отрисовка первого слоя (основного)
        for x in range(self.map.width):
            for y in range(self.map.height):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (
                    x * self.TILE_SIZE + 50, y * self.TILE_SIZE + 50))
        # render player and bullet and mobs
        # for i in self.map.get_objects('walls'):
        #     image = pygame.transform.scale(i.image, (self.TILE_SIZE, self.TILE_SIZE))
        #     screen.blit(image, (i.x / self.map.koeff + 50, i.y / self.map.koeff + 50))

        self.wall_group.draw(screen)
        # Отрисовка второго слоя (деревья и тп)
        for x in range(self.map.width):
            for y in range(self.map.height):
                image = self.map.get_tile_image(x, y, 1)
                if image is not None:
                    screen.blit(image, (
                        x * self.TILE_SIZE + 50, y * self.TILE_SIZE + 50))


fullscreen = False


if __name__ == '__main__':
    clock = pygame.time.Clock()
    running = True
    game = Game(1, 1)
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
        game.render()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
