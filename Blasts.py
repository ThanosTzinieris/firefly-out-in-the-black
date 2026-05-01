from Game_Objects import Game_Object


class Blast(Game_Object):
    def __init__(self, settings, screen, image_path, shooter_type, spawn_x, spawn_y):
        super().__init__(settings, screen, None, None, image_path)

        self.moving = False

        self.shooter_type = shooter_type  # Serenity or Reaver

        # Initialize spawn position in logical space
        self.rect.centerx = spawn_x
        self.rect.centery = spawn_y

        self.rel_pos_x = self.rect.centerx / self.settings.logical_width
        self.rel_pos_y = self.rect.centery / self.settings.logical_height

        #Set movement direction based on shooter type
        self.direction = -1 if self.shooter_type == "Serenity" else 1


    def update(self):
        # Logical movement speed (independent of screen size)
        self.speed_factor = self.settings.logical_height * 0.008

        if self.moving:
            self.rect.centery += self.speed_factor * self.direction
            self.rel_pos_y = self.rect.centery / self.settings.logical_height

        if self.rect.bottom < 0 or self.rect.top > self.settings.logical_height:
            return False  # Signal that the blast should be removed

        return True  # Keep the blast