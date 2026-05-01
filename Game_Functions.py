import sys
import pygame
import random
from Reavers import Reaver
SCORE_FILE = None


# -----------------------------
# ACTIVE RENDER REGISTRY
# -----------------------------
def clear_active_render_groups(settings):
    settings.active_render_groups.clear()


def register_render_groups(settings, groups):
    settings.active_render_groups.extend(groups)


# -----------------------------
# MOUSE REMAPPING
# -----------------------------
def screen_to_logical(pos, settings):
    # Convert screen-space mouse coordinates to logical game coordinates.
    vp = settings.viewport
    x = (pos[0] - vp["x"]) / vp["scale"]
    y = (pos[1] - vp["y"]) / vp["scale"]
    return int(x), int(y)


# ------------------------------------------------
# DISPLAY MODE
# ------------------------------------------------
def apply_display_mode(settings, fullscreen=False, size=None):

    flags = pygame.RESIZABLE

    if fullscreen:
        flags |= pygame.FULLSCREEN
        screen = pygame.display.set_mode((0, 0), flags)
    else:
        if size is None:
            size = (settings.screen_width, settings.screen_height)
        screen = pygame.display.set_mode(size, flags)

    settings.fullscreen = fullscreen

    # Recompute viewport after any display change
    settings.compute_viewport(screen.get_width(), screen.get_height())

    return screen


# -----------------------------
# EVENT HANDLING
# -----------------------------
def check_events(events, screen, settings, game_objects, scoreboard):
    """Handles all game events, including movement, fullscreen toggling, and resizing."""

    for event in events:
        if event.type == pygame.QUIT:
            if settings.score > settings.high_score:
                settings.high_score = settings.score
                save_high_score(settings)
            sys.exit()


        elif event.type == pygame.KEYDOWN:
            # Press 'Left Arrow / A' or 'Right Arrow / D' to start movin'!
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                game_objects["player"]["serenity"].moving_left = True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                game_objects["player"]["serenity"].moving_right = True

            # Press 'Space' to start shootin'!
            elif event.key == pygame.K_SPACE:
                # Skip intro (ONLY in intro state)
                if settings.game_state == "intro":
                    settings.skip_intro = True
                    settings.intro_music_active = False
                    settings.gameplay_music_armed = False  # async no longer needed

                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.gameplay_music)

                    if settings.music_master_on:
                        pygame.mixer.music.play(-1)
                        settings.music_started = True

                # Restart game (ONLY in game_over state)
                if settings.game_state == "game_over":
                    settings.restart_requested = True

                # Fire weapon (ONLY while playing)
                elif settings.game_state == "playing":
                    game_objects["player"]["serenity"].firing = True

            # Press 'F' to toggle fullscreen
            elif event.key == pygame.K_f:
                screen = toggle_fullscreen(screen, settings, game_objects, scoreboard)

            # Press 'M' to toggle music
            elif (
                event.key == pygame.K_m
                and settings.game_state in ("playing", "paused", "game_over")
            ):
                toggle_music(settings)
                game_objects["buttons"]["music"].toggle()

            # Press 'P' or 'Esc' to toggle pause/play
            elif (
                event.key in (pygame.K_p, pygame.K_ESCAPE)
                and settings.game_state in ("playing", "paused")
            ):
                toggle_pause(settings, game_objects)

            # Press Q to exit
            elif (
                event.key == pygame.K_q
                and settings.game_state in ("paused", "game_over")
            ):
                pygame.quit()
                sys.exit()


        elif event.type == pygame.KEYUP:
            # Stop pressing 'Arrows / A / D' to stay still
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                game_objects["player"]["serenity"].moving_left = False
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                game_objects["player"]["serenity"].moving_right = False

            # Stop pressing 'Space' to cease fire
            elif event.key == pygame.K_SPACE:
                game_objects["player"]["serenity"].firing = False

        elif event.type == pygame.VIDEORESIZE and not settings.fullscreen:
            resize_screen(event.w, event.h, settings, scoreboard)

        # Button toggling
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = screen_to_logical(event.pos, settings)

            # Music button toggle (clickable even while paused)
            if (
                settings.game_state in ("playing", "paused", "game_over")
                and game_objects["buttons"]["music"].rect.collidepoint(mouse_pos)
            ):
                toggle_music(settings)
                game_objects["buttons"]["music"].toggle() # Switch button image

            # Pause/Play button toggle
            elif (
                settings.game_state in ("playing", "paused")
                and game_objects["buttons"]["pause"].rect.collidepoint(mouse_pos)
            ):
                toggle_pause(settings, game_objects)

            # Quit button click
            elif (
                settings.game_state in ("paused", "game_over")
                and game_objects["buttons"]["quit"].rect.collidepoint(mouse_pos)
            ):
                pygame.quit()
                sys.exit()


# -----------------------------
# STATE HANDLING
# -----------------------------
def enter_state(settings, new_state):
    if settings.game_state == new_state:
        return

    previous_state = settings.game_state
    settings.game_state = new_state

    # -----------------------------
    # STATE ENTRY: INTRO
    # -----------------------------
    if new_state == "intro":
        # Register intro objects
        clear_active_render_groups(settings)
        from Intro_Sequence import get_intro_objects
        register_render_groups(settings, get_intro_objects())

        settings.intro_music_active = True
        settings.gameplay_music_armed = False
        play_music(settings, settings.intro_music, 0)

    # -----------------------------
    # STATE ENTRY: PLAYING
    # -----------------------------
    elif new_state == "playing":

        # Register gameplay objects
        clear_active_render_groups(settings)
        register_render_groups(settings, settings.playing_groups)

        # Coming back from pause → resume ONLY
        if previous_state == "paused":
            if settings.music_master_on and settings.music_started:
                pygame.mixer.music.unpause()

        # Fresh entry into playing (restart, game over → playing, intro → playing)
        else:
            # Do NOT touch music here if async intro handoff is in effect
            if not settings.intro_music_active and not settings.gameplay_music_armed:
                play_music(settings, settings.gameplay_music, -1)

    # -----------------------------
    # STATE ENTRY: PAUSED
    # -----------------------------
    elif new_state == "paused":
        if settings.music_started:
            pygame.mixer.music.pause()

    # -----------------------------
    # STATE ENTRY: GAME OVER
    # -----------------------------
    elif new_state == "game_over":
        play_music(settings, settings.game_over_music, 0)

        # Update and save high score
        if settings.score > settings.high_score:
            settings.high_score = settings.score
            save_high_score(settings)

# -----------------------------
# MUSIC
# -----------------------------
def play_music(settings, music_path, loops):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(music_path)
    settings.music_started = False

    if settings.music_master_on:
        pygame.mixer.music.play(loops)
        settings.music_started = True

def toggle_music(settings):
    # Flip master switch
    settings.music_master_on = not settings.music_master_on

    # -------------------------
    # MASTER OFF → always pause
    # -------------------------
    if not settings.music_master_on:
        pygame.mixer.music.pause()
        return

    # -------------------------
    # MASTER ON
    # -------------------------

    # If game is paused → DO NOTHING
    if settings.game_state == "paused":
        return

    # If music has never started → start it
    if not settings.music_started:
        pygame.mixer.music.play(-1)
        settings.music_started = True
    else:
        pygame.mixer.music.unpause()


def toggle_pause(settings, game_objects):

    if settings.game_state == "playing":
        enter_state(settings, "paused")
    else:
        enter_state(settings, "playing")

    game_objects["buttons"]["pause"].toggle()  # Switch pause/play button image


def spawn_reaver_wave(settings, screen, level):
    reavers = []

    for slot_id in settings.LEVELS[level]:
        rx, ry = settings.REAVER_SLOTS[slot_id]

        reaver_skin = random.choice(settings.REAVERS)

        reaver = Reaver(
            settings,
            screen,
            rx,
            ry,
            reaver_skin,
            settings.REAVER_ALT
        )

        reavers.append(reaver)

    return reavers


def spawn_random_reaver_wave(settings, screen):
    reavers = []

    slot_count = random.randint(5, len(settings.REAVER_SLOTS))
    chosen_slots = random.sample(
        list(settings.REAVER_SLOTS.keys()),
        slot_count
    )

    for slot_id in chosen_slots:
        rx, ry = settings.REAVER_SLOTS[slot_id]

        reaver_skin = random.choice(settings.REAVERS)

        reaver = Reaver(
            settings,
            screen,
            rx,
            ry,
            reaver_skin,
            settings.REAVER_ALT
        )

        reavers.append(reaver)

    return reavers


def masks_collide(obj_a, obj_b):
    # Returns True if obj_a and obj_b collide using rect + mask.
    # Assumes both objects have: rect and active_mask.

    if not obj_a.rect.colliderect(obj_b.rect):
        return False

    offset = (
        obj_b.rect.left - obj_a.rect.left,
        obj_b.rect.top  - obj_a.rect.top
    )

    return obj_a.active_mask.overlap(obj_b.active_mask, offset) is not None


def check_serenity_meteor_collision(serenity, meteors, settings):
    for meteor in meteors:
        if masks_collide(serenity, meteor):

            if not settings.impact_active:
                settings.impact_active = True
                settings.impact_start_time = pygame.time.get_ticks()
                settings.impact_meteor = meteor

            return


def check_plasma_meteor_collisions(plasma_blasts, meteors):
    for blast in plasma_blasts[:]:
        for meteor in meteors:
            if masks_collide(blast, meteor):

                meteor.explode()
                meteor.remove_after_frames = 5

                plasma_blasts.remove(blast)
                return


def check_plasma_reaver_collisions(plasma_blasts, reavers, settings):
    for blast in plasma_blasts[:]:
        for reaver in reavers[:]:
            if masks_collide(blast, reaver):

                if reaver.state == "active":
                    reaver.explode()
                    reaver.state = "dying"
                    reaver.remove_after_frames = 5

                    settings.score += 1


def check_harpoon_serenity_collision(harpoons, serenity, settings):
    for harpoon in harpoons:
        if masks_collide(harpoon, serenity):

            if not settings.impact_active:
                settings.impact_active = True
                settings.impact_start_time = pygame.time.get_ticks()
                settings.impact_meteor = None

            return

# -----------------------------
# UTILITY ZONE
# -----------------------------
def toggle_fullscreen(screen, settings, game_objects, scoreboard):
    if settings.fullscreen:
        # Exit fullscreen → restore windowed size
        screen = apply_display_mode(
            settings,
            fullscreen=False,
            size=(settings.screen_width, settings.screen_height)
        )
    else:
        # Enter fullscreen
        screen = apply_display_mode(settings, fullscreen=True)

    # Notify all objects of display-mode change
    for group in game_objects.values():
        if isinstance(group, dict):
            for obj in group.values():
                obj.resize()
        else:
            for obj in group:
                obj.resize()

    scoreboard.rebuild()

    return screen


def resize_screen(new_width, new_height, settings, scoreboard):
  
    if abs(new_width - settings.screen_width) > abs(new_height - settings.screen_height):
        new_height = round(new_width / settings.aspect_ratio)
    else:
        new_width = round(new_height * settings.aspect_ratio)
    
    settings.screen_width, settings.screen_height = new_width, new_height

    # Apply resize via unified display pipeline (side effects only)
    apply_display_mode(settings, fullscreen=False, size=(new_width, new_height))

    scoreboard.rebuild()


def load_high_score(settings):
    try:
        with open(settings.SCORES_DIR / "high_score.txt", "r") as f:
            settings.high_score = int(f.read())
    except (FileNotFoundError, ValueError):
        settings.high_score = 0


def save_high_score(settings):
    with open(settings.SCORES_DIR / "high_score.txt", "w") as f:
        f.write(str(settings.high_score))