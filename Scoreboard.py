import pygame


class Scoreboard:
    def __init__(self, settings, screen):
        self.settings = settings
        self.screen = screen

        self.font_path = settings.ASSETS_DIR / "Fonts" / "PAPYRUS.TTF"
        self.color = (255, 255, 255)

        self.font = None
        self.image = None
        self.rect = None
        self.last_score = None

        self.rebuild()


    def rebuild(self):
        vp = self.settings.viewport

        font_px = int(vp["height"] * 0.030)
        self.font = pygame.font.Font(self.font_path, font_px)

        current_val = self.settings.score
        high_val    = self.settings.high_score

        display_high = max(current_val, high_val)

        current = f"{current_val:05d}"
        high    = f"{display_high:05d}"

        line1 = current
        line2 = f"/{high}"

        self.img_top = self.font.render(line1, True, self.color)
        self.img_bot = self.font.render(line2, True, self.color)

        self.rect_top = self.img_top.get_rect()
        self.rect_bot = self.img_bot.get_rect()

        right = vp["x"] + int(vp["width"] * 0.97)
        top   = vp["y"] + int(vp["width"] * 0.02)

        self.rect_top.topright = (right, top)
        self.rect_bot.topright = (right, self.rect_top.bottom)


    def update(self):
        if self.settings.score != self.last_score:
            self.last_score = self.settings.score
            self.rebuild()


    def draw(self):
        self.screen.blit(self.img_top, self.rect_top)
        self.screen.blit(self.img_bot, self.rect_bot)