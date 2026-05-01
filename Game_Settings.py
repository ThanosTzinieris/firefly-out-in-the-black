import pygame
from pathlib import Path


class Settings():
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent

        self.title = "Firefly: Out in the Black"
        
        self.clock = pygame.time.Clock()

        # -----------------------------------------------------------
        # Logical (internal) game resolution
        # -----------------------------------------------------------
        self.logical_width  = 1920
        self.logical_height = 1080

        # -----------------------------------------------------------
        # Viewport (logical → screen mapping)
        # -----------------------------------------------------------
        self.viewport = {
            "x": 0,
            "y": 0,
            "width": self.logical_width,
            "height": self.logical_height,
            "scale": 1.0,
        }

        self.aspect_ratio = 16 / 9

        # Default windowed startup size (used when fullscreen = False)
        self.screen_width = 1280
        self.screen_height = int(self.screen_width / self.aspect_ratio)


        # -----------------------------------------------------------
        # Flag Hoisting
        # -----------------------------------------------------------
        self.fullscreen = True
        self.game_state = None
        self.restart_requested = False
        self.music_started = False
        self.intro_music_active = False
        self.gameplay_music_armed = False
        self.skip_intro = False
        self.serenity_entry_done = False

        # Impact / collision phase:
        self.impact_active = False
        self.impact_start_time = 0
        self.impact_duration_ms = 50


        # ----------------------------------------
        # Score System
        # ----------------------------------------
        self.score = 0
        self.high_score = 0
        self.score_file_path = None  # set later


        # -----------------------------------------------------------
        # Active render registry (engine-owned)
        # -----------------------------------------------------------
        self.active_render_groups = []


        # -----------------------------------------------------------
        # Pathfinder
        # -----------------------------------------------------------
        self.ASSETS_DIR = self.BASE_DIR / "Assets"
        self.SCORES_DIR = self.BASE_DIR / "Scores"

        # Asset subfolders
        self.SHIPS_DIR      = self.ASSETS_DIR / "Ships"
        self.METEORS_DIR    = self.ASSETS_DIR / "Meteors"
        self.BUTTONS_DIR    = self.ASSETS_DIR / "Buttons"
        self.SURFACES_DIR   = self.ASSETS_DIR / "Surfaces"
        self.CINEMATICS_DIR = self.ASSETS_DIR / "Cinematics"
        self.SOUNDS_DIR     = self.ASSETS_DIR / "Soundscapes"

        # -----------------------------------------------------------
        # Path Clearing
        # -----------------------------------------------------------
        self.ASSETS_DIR.mkdir(exist_ok=True)
        self.SCORES_DIR.mkdir(exist_ok=True)

        self.SHIPS_DIR.mkdir(exist_ok=True)
        self.METEORS_DIR.mkdir(exist_ok=True)
        self.BUTTONS_DIR.mkdir(exist_ok=True)
        self.SURFACES_DIR.mkdir(exist_ok=True)
        self.CINEMATICS_DIR.mkdir(exist_ok=True)
        self.SOUNDS_DIR.mkdir(exist_ok=True)


        # -----------------------------------------------------------
        # Image Loading Bay
        # -----------------------------------------------------------

        # Ships
        self.SERENITY      = self.SHIPS_DIR / "Serenity.png"
        self.SERENITY_ALT  = self.SHIPS_DIR / "Serenity_Alt.png"
        self.PLASMA_BLAST  = self.SHIPS_DIR / "Plasma_Blast.png"
        # Reavers (12 main skins, 1 shared alt)
        self.REAVERS = [
            self.SHIPS_DIR / "Reaver_1.png",
            self.SHIPS_DIR / "Reaver_2.png",
            self.SHIPS_DIR / "Reaver_3.png",
            self.SHIPS_DIR / "Reaver_4.png",
            self.SHIPS_DIR / "Reaver_5.png",
            self.SHIPS_DIR / "Reaver_6.png",
            self.SHIPS_DIR / "Reaver_7.png",
            self.SHIPS_DIR / "Reaver_8.png",
            self.SHIPS_DIR / "Reaver_9.png",
            self.SHIPS_DIR / "Reaver_10.png",
            self.SHIPS_DIR / "Reaver_11.png",
            self.SHIPS_DIR / "Reaver_12.png",
        ]
        self.REAVER_ALT    = self.SHIPS_DIR / "Reaver_Alt.png"
        self.HARPOON       = self.SHIPS_DIR / "Harpoon.png"
        # Meteors
        self.METEORS = [
            self.METEORS_DIR / "Meteor_01.png",
            self.METEORS_DIR / "Meteor_02.png",
            self.METEORS_DIR / "Meteor_03.png",
            self.METEORS_DIR / "Meteor_04.png",
            self.METEORS_DIR / "Meteor_05.png",
        ]
        self.DEBRIS = self.METEORS_DIR / "Meteor_Debris.png"
        # Buttons
        self.MUSIC_ON  = self.BUTTONS_DIR / "Music.png"
        self.MUSIC_OFF = self.BUTTONS_DIR / "MusicOff.png"
        self.PAUSE     = self.BUTTONS_DIR / "Pause.png"
        self.PLAY      = self.BUTTONS_DIR / "Play.png"
        self.QUIT      = self.BUTTONS_DIR / "Quit.png"
        # Surfaces
        self.GAME_ICON = self.SURFACES_DIR / "game_icon.png"
        self.BACKGROUND = self.SURFACES_DIR / "Background.png"
        self.GAME_OVER  = self.SURFACES_DIR / "Game_Over.png"
        self.CONTROLS   = self.SURFACES_DIR / "Controls.png"
        # Cinematics (Intro)
        self.INTRO_1   = self.CINEMATICS_DIR / "Intro1.png"
        self.INTRO_2   = self.CINEMATICS_DIR / "Intro2.png"
        self.INTRO_BG  = self.CINEMATICS_DIR / "Intro_bg.png"
        self.INTRO_TEXTBOXES = [
            self.CINEMATICS_DIR / "1.png",
            self.CINEMATICS_DIR / "2.png",
            self.CINEMATICS_DIR / "3.png",
            self.CINEMATICS_DIR / "4.png",
            self.CINEMATICS_DIR / "5.png",
            self.CINEMATICS_DIR / "6.png",
        ]


        # -----------------------------------------------------------
        # Reaver Formation Slots
        # Logical-space relative positions (center-based)
        # Authored for 1920x1080, sprite size 71x100
        # -----------------------------------------------------------
        self.REAVER_SLOTS = {
            # Row 1
            1:  (0.13, 0.09),
            2:  (0.23, 0.09),
            3:  (0.32, 0.09),
            4:  (0.41, 0.09),
            5:  (0.50, 0.09),  # center
            6:  (0.59, 0.09),
            7:  (0.68, 0.09),
            8:  (0.78, 0.09),
            9:  (0.87, 0.09),

            # Row 2
            10: (0.18, 0.24),
            11: (0.27, 0.24),
            12: (0.36, 0.24),
            13: (0.45, 0.24),
            14: (0.55, 0.24),
            15: (0.64, 0.24),
            16: (0.73, 0.24),
            17: (0.82, 0.24),
        }

        # -----------------------------------------------------------
        # Reaver Formation Configurations / Levels
        # -----------------------------------------------------------
        self.LEVELS = {
            1: [3, 4, 5, 6, 7],
            2: [1, 3, 5, 7, 9],
            3: [1, 2, 4, 5, 6, 8, 9],
            4: list(range(1, 10)),
            5: [3, 4, 5, 6, 7, 12, 13, 14, 15],
            6: [2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16],
            7: list(range(1, 18)), # full pack (17)
        }


        # ----------------------------------------
        # Soundscapes
        # ----------------------------------------
        self.intro_music    = self.SOUNDS_DIR / "Intro.ogg"
        self.gameplay_music = self.SOUNDS_DIR / "Gameplay.ogg"
        self.game_over_music= self.SOUNDS_DIR / "Game_Over.ogg"

        self.current_music = self.gameplay_music
        self.music_master_on = True


        # ----------------------------------------
        # Meteor Spawning & Speed Multiplier
        # ----------------------------------------
        self.METEOR_SPAWN_INTERVAL_MS = 5000   # 5 seconds
        self.METEOR_SPAWN_PROBABILITY = 0.5    # 50% chance

        # Timestamp of last meteor spawn attempt
        self.last_meteor_spawn = 0

        self.METEOR_SPEED_MIN = 0.006
        self.METEOR_SPEED_MAX = 0.009


    def compute_viewport(self, screen_width, screen_height):
        # ----------------------------------------
        # Compute viewport rectangle that preserves aspect ratio
        # and fits the logical resolution inside the screen.
        # ----------------------------------------
        scale_x = screen_width  / self.logical_width
        scale_y = screen_height / self.logical_height

        # Use the smaller scale to preserve aspect ratio
        scale = min(scale_x, scale_y)

        viewport_width  = int(self.logical_width  * scale)
        viewport_height = int(self.logical_height * scale)

        viewport_x = (screen_width  - viewport_width)  // 2
        viewport_y = (screen_height - viewport_height) // 2

        self.viewport["x"] = viewport_x
        self.viewport["y"] = viewport_y
        self.viewport["width"]  = viewport_width
        self.viewport["height"] = viewport_height
        self.viewport["scale"]  = scale