from Game_Objects import Game_Object

class Button(Game_Object):
    def __init__(self, settings, screen, main_image_path, toggled_image_path, rel_pos_x, rel_pos_y):

        # Initialize superclass with main and alt image
        super().__init__(settings, screen, rel_pos_x, rel_pos_y, main_image_path, alt_image_path=toggled_image_path)

        # Spawn position in logical space
        self.rect.centerx = int(self.settings.logical_width  * self.rel_pos_x)
        self.rect.centery = int(self.settings.logical_height * self.rel_pos_y)

        # Flag hoisting
        self.is_toggled = False


    def toggle(self):
        # Toggles
        self.is_toggled = not self.is_toggled
        if self.is_toggled and hasattr(self, "alt_scaled") and self.alt_scaled:
            self.active_image = self.alt_scaled
        else:
            self.active_image = self.main_scaled