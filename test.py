import pygame as pg

import pygame.examples.eventlist
pygame.examples.eventlist.main()
pygame.key


def change_alpha(orig_surf, alpha):
    """Create a copy of orig_surf with the desired alpha value.

    This function creates another surface with the desired alpha
    value and then blits it onto the copy of the original surface
    with the `BLEND_RGBA_MULT` flag to change the transparency."""
    surf = orig_surf.copy()
    # This surface is used to adjust the alpha of the txt_surf.
    alpha_surf = pg.Surface(surf.get_size(), pg.SRCALPHA)
    alpha_surf.fill((255, 255, 255, alpha))  # Set the alpha value.
    surf.blit(alpha_surf, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return surf


def main():
    clock = pg.time.Clock()
    screen = pg.display.set_mode((640, 480))
    font = pg.font.Font(None, 64)

    # The original surface which will never be modified.
    orig_surf = font.render('Enter your text', True, pg.Color('dodgerblue'))
    alpha = 255  # The current alpha value of the surface.

    # Surface 2
    orig_surf2 = font.render('Another text surface', True, pg.Color('sienna1'))
    alpha2 = 0

    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        if alpha > 0:
            # Reduce alpha each frame.
            alpha -= 4
            alpha = max(0, alpha)  # Make sure it doesn't go below 0.
            surf = change_alpha(orig_surf, alpha)
        if alpha2 < 255:
            alpha2 += 4
            alpha2 = min(255, alpha2)
            surf2 = change_alpha(orig_surf2, alpha2)

        screen.fill((30, 30, 30))
        screen.blit(surf, (30, 60))
        screen.blit(surf2, (30, 60))
        pg.display.flip()
        clock.tick(30)


# if __name__ == '__main__':
#     pg.init()
#     main()
#     pg.quit()
