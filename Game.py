import pygame
from Game_Settings import Settings
from Game_Objects import Game_Object
import Intro_Sequence as intro
import Game_Functions as gf
from Ship import Firefly
from Buttons import Button
from Meteors import Meteor
from Scoreboard import Scoreboard
import random

# ------------------------------------------------
# ---------- FIREFLY: OUT IN THE BLACK -----------
# ------------------------------------------------


# ------------------------------------------------
# Helper Functions
# ------------------------------------------------
def maybe_spawn_meteor(meteors, settings, screen, now):
    if now - settings.last_meteor_spawn >= settings.METEOR_SPAWN_INTERVAL_MS:
        settings.last_meteor_spawn = now

        if random.random() < settings.METEOR_SPAWN_PROBABILITY:
            meteor_image = random.choice(settings.METEORS)
            meteors.append(Meteor(settings, screen, meteor_image))


def reset_game_state(settings, screen, scoreboard, game_objects):
    pygame.mixer.music.stop()
    settings.music_started = False
    settings.intro_music_active = False
    settings.gameplay_music_armed = False

    settings.last_meteor_spawn = 0
    settings.score = 0
    scoreboard.last_score = None
    settings.impact_active = False
    settings.impact_start_time = 0
    settings.impact_meteor = None

    serenity = Firefly(settings, screen, settings.SERENITY, settings.SERENITY_ALT)
    game_objects["player"]["serenity"] = serenity

    game_objects["meteors"].clear()
    game_objects["plasma"].clear()
    game_objects["harpoons"].clear()

    game_objects["reavers"].clear()
    game_objects["reavers"].extend(
        gf.spawn_reaver_wave(settings, screen, 1)
    )

    return serenity

def render_frame(screen, settings, background, controls, buttons, serenity,
                 reavers, plasma_blasts, harpoons, meteors, game_over, scoreboard):

        if settings.game_state != "intro":

            screen.fill((0, 0, 0))

            vp = settings.viewport
            screen.set_clip(pygame.Rect(
                vp["x"],
                vp["y"],
                vp["width"],
                vp["height"]
            ))

            background.blitme()

            for button in buttons:
                button.blitme()

            for harpoon in harpoons:
                harpoon.blitme()

            if serenity.state == "entering":
                controls.blitme()

            serenity.blitme()

            for reaver in reavers:
                reaver.blitme()

            for blast in plasma_blasts:
                blast.blitme()

            for meteor in meteors:
                meteor.blitme()
            
            if settings.game_state == "game_over":
                game_over.blitme()

        screen.set_clip(None)  # restore full-screen drawing

        scoreboard.update()
        if settings.game_state in ("playing", "paused", "game_over"):
            scoreboard.draw()

        pygame.display.flip()

# ------------------------------------------------
# Main Game Function
# ------------------------------------------------

def run_game():
    pygame.init()
    settings = Settings()

    icon_surface = pygame.image.load(settings.GAME_ICON)
    pygame.display.set_icon(icon_surface)

    gf.load_high_score(settings)

    current_level = 1
    max_level = max(settings.LEVELS.keys())

    screen = gf.apply_display_mode(settings, fullscreen=settings.fullscreen)

    scoreboard = Scoreboard(settings, screen)

    background = Game_Object(settings, screen, 0.5, 0.5, settings.BACKGROUND)

    controls = Game_Object(settings, screen, 0.5, 0.5, settings.CONTROLS)
 
    serenity = Firefly(settings, screen, settings.SERENITY, settings.SERENITY_ALT)

    music_button = Button(settings, screen, settings.MUSIC_ON, settings.MUSIC_OFF, 0.04, 0.07)
    pause_button = Button(settings, screen, settings.PAUSE, settings.PLAY, 0.04, 0.15)
    quit_button = Button(settings, screen, settings.QUIT, None, 0.05, 0.93)

    game_over = Game_Object(settings, screen, 0.5, 0.5, settings.GAME_OVER)

    pygame.display.set_caption(settings.title)

    reavers = gf.spawn_reaver_wave(settings, screen, current_level)

    meteors = []

    plasma_blasts = []
    harpoons = []

    game_objects = {
        "player":     {"serenity": serenity},
        "plasma":     plasma_blasts,
        "reavers":    reavers,
        "harpoons":   harpoons,
        "meteors":    meteors,
        "buttons":    {
            "music": music_button,
            "pause": pause_button,
            "quit" : quit_button
        },
        "background": [background],
        "game_over":  [game_over],
    }

    settings.playing_groups = list(game_objects.values())

    gf.enter_state(settings, "intro")


    while True:
        events = pygame.event.get()

        gf.check_events(events, screen, settings, game_objects, scoreboard)

        # --------------------------------
        # RESTART HANDLING
        # --------------------------------
        if settings.restart_requested:
            settings.restart_requested = False
            serenity = reset_game_state(settings, screen, scoreboard, game_objects)
            current_level = 1
            gf.enter_state(settings, "playing")


        # --------------------------------
        # GAME STATES
        # --------------------------------

        # INTRO
        if settings.game_state == "intro":
            still_running = intro.update_and_draw(screen, settings)
            if not still_running:
                settings.gameplay_music_armed = True
                gf.enter_state(settings, "playing")

        # PLAYING
        elif settings.game_state == "playing":

            # Async Music Handoff (Intro → Gameplay)
            if (
                settings.intro_music_active
                and settings.gameplay_music_armed
                and not pygame.mixer.music.get_busy()
                and settings.music_master_on
            ):
                pygame.mixer.music.load(settings.gameplay_music)
                pygame.mixer.music.play(-1)

                settings.music_started = True
                settings.intro_music_active = False
                settings.gameplay_music_armed = False

            # Impact aftermath
            if settings.impact_active:
                now = pygame.time.get_ticks()
                if now - settings.impact_start_time >= settings.impact_duration_ms:
                    settings.impact_active = False

                    # Final impact visuals
                    serenity.explode()

                    if settings.impact_meteor:
                        settings.impact_meteor.explode()
                        settings.impact_meteor = None

                    gf.enter_state(settings, "game_over")

            now = pygame.time.get_ticks()

            maybe_spawn_meteor(meteors, settings, screen, now)

            # Serenity firing
            if serenity.firing:
                blast1, blast2 = serenity.fire()
                if blast1:
                    plasma_blasts.append(blast1)
                    plasma_blasts.append(blast2)

            for blast in plasma_blasts[:]:
                if not blast.update():
                    plasma_blasts.remove(blast)

            gf.check_plasma_meteor_collisions(plasma_blasts, meteors)

            # Reavers
            for reaver in reavers[:]:
                result = reaver.update()

                if result is False:
                    reavers.remove(reaver)
                elif result:
                    harpoons.append(result)

            for harpoon in harpoons[:]:
                if not harpoon.update():
                    harpoons.remove(harpoon)

            gf.check_plasma_reaver_collisions(plasma_blasts, reavers, settings)

            # --------------------------------
            # LEVEL CLEAR CHECK
            # --------------------------------
            if not reavers:
                current_level += 1

                if current_level <= max_level:
                    reavers.extend(
                        gf.spawn_reaver_wave(settings, screen, current_level)
                    )
                else:
                    reavers.extend(
                        gf.spawn_random_reaver_wave(settings, screen)
                    )

            gf.check_harpoon_serenity_collision(harpoons, serenity, settings)

            serenity.update()

            for meteor in meteors[:]:
                if not meteor.update():
                    meteors.remove(meteor)

            gf.check_serenity_meteor_collision(serenity, meteors, settings)

        # --------------------------------
        # RENDERING
        # --------------------------------
        active_buttons = [music_button, pause_button]

        if settings.game_state in ("paused", "game_over"):
            active_buttons.append(quit_button)

        render_frame(
            screen,
            settings,
            background,
            controls,
            active_buttons,
            serenity,
            reavers,
            plasma_blasts,
            harpoons,
            meteors,
            game_over,
            scoreboard
        )

        settings.clock.tick(60)

if __name__ == "__main__":
    run_game()