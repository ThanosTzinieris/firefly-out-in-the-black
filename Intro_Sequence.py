import pygame
from Game_Objects import Game_Object


# -------------------------------------------------
# BLIT THROUGH VIEWPORT
# -------------------------------------------------
def blit_intro(surface, image, settings, x=0, y=0):

    vp = settings.viewport
    scale = vp["scale"]

    scaled = pygame.transform.smoothscale(
        image,
        (
            int(image.get_width() * scale),
            int(image.get_height() * scale),
        )
    )

    screen_x = vp["x"] + int(x * scale)
    screen_y = vp["y"] + int(y * scale)

    surface.blit(scaled, (screen_x, screen_y))


# -------------------------------------------------
# INTRO STORAGE
# -------------------------------------------------
intro_data = {
    "initialized": False,
    "start_time": None,
    "objects": None
}


def init_intro(settings, screen):
    global intro_data

    if intro_data["initialized"]:
        return

    # SINGLE, GLOBAL INTRO CLOCK
    intro_data["start_time"] = pygame.time.get_ticks()

    # ---------- LOAD OBJECTS ----------
    intro1 = Game_Object(settings, screen, 0.5, 0.5, settings.INTRO_1)
    intro2 = Game_Object(settings, screen, 0.5, 0.5, settings.INTRO_2)
    bg     = Game_Object(settings, screen, 0.5, 0.5, settings.INTRO_BG)
    textboxes = [
        Game_Object(settings, screen, 0, 0, path)
        for path in settings.INTRO_TEXTBOXES
    ]


    rel_positions = [
        (0.23, 0.70),
        (0.75, 0.64),
        (0.47, 0.57),
        (0.76, 0.63),
        (0.23, 0.70),
        (0.76, 0.61),
    ]

    for tb, (rx, ry) in zip(textboxes, rel_positions):
        tb.rel_pos_x = rx
        tb.rel_pos_y = ry
        tb.rect.centerx = int(settings.logical_width  * rx)
        tb.rect.centery = int(settings.logical_height * ry)

    intro_objects = [[intro1], [intro2], [bg]] + [[tb] for tb in textboxes]

    intro_data["objects"] = {
        "intro1": intro1,
        "intro2": intro2,
        "bg": bg,
        "textboxes": textboxes,
        "packed": intro_objects
    }

    intro_data["initialized"] = True

    from Game_Functions import clear_active_render_groups, register_render_groups
    clear_active_render_groups(settings)
    register_render_groups(settings, intro_data["objects"]["packed"])


# -------------------------------------------------
# INTRO SCRIPT
# -------------------------------------------------
def update_and_draw(screen, settings):
    # Ensure intro is initialized once
    init_intro(settings, screen)

    intro_start_time = intro_data["start_time"]

    intro1 = intro_data["objects"]["intro1"]
    intro2 = intro_data["objects"]["intro2"]
    bg     = intro_data["objects"]["bg"]
    textboxes = intro_data["objects"]["textboxes"]

    # Handle skip (flag is set by main event loop)
    if settings.skip_intro:
        settings.skip_intro = False
        return False

    now = pygame.time.get_ticks() - intro_start_time

    screen.fill((0, 0, 0))

    # -------------------------------------------------
    # INTRO 1 FADE IN (00:00 → 02:00)
    # -------------------------------------------------
    if 0 <= now < 2000:
        alpha = int(255 * (now / 2000))
        s1 = intro1.main_scaled.copy()
        s1.set_alpha(alpha)
        blit_intro(screen, s1, settings)

    # -------------------------------------------------
    # INTRO 1 HOLD (02:00 → 03:30)
    # -------------------------------------------------
    elif 2000 <= now < 3500:
        blit_intro(screen, intro1.main_scaled, settings)

    # -------------------------------------------------
    # INTRO 2 FADE IN (03:30 → 04:48)
    # -------------------------------------------------
    elif 3500 <= now < 4800:
        blit_intro(screen, intro1.main_scaled, settings)
        alpha = int(255 * ((now - 3500) / 1300))
        s2 = intro2.main_scaled.copy()
        s2.set_alpha(alpha)
        blit_intro(screen, s2, settings)

    # -------------------------------------------------
    # BOTH HOLD (04:48 → 05:30)
    # -------------------------------------------------
    elif 4800 <= now < 5500:
        blit_intro(screen, intro1.main_scaled, settings)
        blit_intro(screen, intro2.main_scaled, settings)

    # -------------------------------------------------
    # BOTH FADE OUT (05:30 → 07:30)
    # -------------------------------------------------
    elif 5500 <= now < 7500:
        alpha = 255 - int(255 * ((now - 5500) / 2000))
        s1 = intro1.main_scaled.copy(); s1.set_alpha(alpha)
        s2 = intro2.main_scaled.copy(); s2.set_alpha(alpha)
        blit_intro(screen, s1, settings)
        blit_intro(screen, s2, settings)

    # -------------------------------------------------
    # BACKGROUND FADE IN (08:00 → 10:30)
    # -------------------------------------------------
    elif 8000 <= now < 10300:
        alpha = int(255 * ((now - 8000) / 2300))
        s_bg = bg.main_scaled.copy()
        s_bg.set_alpha(alpha)
        blit_intro(screen, s_bg, settings)

    # -------------------------------------------------
    # BACKGROUND HOLD + TEXTBOX SEQUENCE
    # -------------------------------------------------
    elif 10300 <= now < 33217:
        blit_intro(screen, bg.main_scaled, settings)

        TB_WINDOWS = [
            (10633, 14117, 0),
            (14517, 19850, 1),
            (20250, 23533, 2),
            (23933, 26917, 3),
            (27317, 29817, 4),
            (30217, 33217, 5),
        ]

        for start, end, idx in TB_WINDOWS:
            if start <= now < end:
                tb = textboxes[idx]
                blit_intro(
                    screen,
                    tb.main_scaled,
                    settings,
                    tb.rect.left,
                    tb.rect.top
                )
                break

    # -------------------------------------------------
    # BACKGROUND FADE OUT (33:13 → 35:00)
    # -------------------------------------------------
    elif 33217 <= now < 35000:
        alpha = 255 - int(255 * ((now - 33217) / 1783))
        s_bg = bg.main_scaled.copy()
        s_bg.set_alpha(alpha)
        blit_intro(screen, s_bg, settings)

    # -------------------------------------------------
    # INTRO DONE
    # -------------------------------------------------
    elif now >= 35000:
        return False

    return True


# -------------------------------------------------
# PACKING HELPER
# -------------------------------------------------
def get_intro_objects():
    if not intro_data["initialized"]:
        return []
    return intro_data["objects"]["packed"]